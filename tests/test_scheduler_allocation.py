"""Scarcity qualification, competing predictions, and complete CPU accounting."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from orthopolity.scheduler_allocation import (
    allocation_predictions, cgroup_cpu_limits, conditional_design, dense_job,
    duty_constrained_rates, hardware_gate, parse_cpu_max, summarize_trial,
)


ROOT=Path(__file__).resolve().parents[1]


class SchedulerChecks(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'configs/scheduler_allocation_2026-10-01.json').read_text())
        self.capacity=dict(capacity_constraints=[dict(kind='logical_cpu_count',capacity_cpus=10.)],
                           inherited_scheduler_policy=None)

    def test_ten_cores_cannot_qualify_three_workers_as_scarce(self):
        gate=hardware_gate(self.config,self.capacity)
        self.assertFalse(gate['eligible'])
        self.assertFalse(gate['changes_to_priority_affinity_or_cgroups'])
        constrained=deepcopy(self.capacity)
        constrained['capacity_constraints'].append(dict(kind='inherited_affinity',capacity_cpus=2.))
        self.assertTrue(hardware_gate(self.config,constrained)['eligible'])
        constrained['inherited_scheduler_policy']=1
        self.assertFalse(hardware_gate(self.config,constrained)['eligible'])

    def test_cpu_quota_requires_short_period_and_no_burst(self):
        capacity=deepcopy(self.capacity)
        quota=dict(kind='cgroup_cpu_quota',capacity_cpus=1.5,
                   period_microseconds=100000,burst_microseconds=0)
        capacity['capacity_constraints'].append(quota)
        self.assertTrue(hardware_gate(self.config,capacity)['eligible'])
        quota['burst_microseconds']=1000
        self.assertFalse(hardware_gate(self.config,capacity)['eligible'])
        quota.update(burst_microseconds=0,period_microseconds=1000000)
        self.assertFalse(hardware_gate(self.config,capacity)['eligible'])
        quota.update(period_microseconds=100000,capacity_cpus=3)
        self.assertFalse(hardware_gate(self.config,capacity)['eligible'])

    def test_cgroup_v2_ancestors_and_namespace_mount_are_resolved(self):
        files={'/sys/cgroup/team/task/cpu.max':'max 100000',
               '/sys/cgroup/team/cpu.max':'150000 100000',
               '/sys/cgroup/cpu.max':'200000 100000'}
        def read(path):
            if str(path) not in files:raise FileNotFoundError(str(path))
            return files[str(path)]
        result=cgroup_cpu_limits('0::/tenant/team/task\n',
            '30 20 0:20 /tenant /sys/cgroup rw - cgroup2 cgroup rw\n',read)
        self.assertEqual([r['capacity_cpus'] for r in result['limits']],[1.5,2.])
        self.assertEqual(result['warnings'],[])
        unresolved=cgroup_cpu_limits('0::/different/task\n',
            '30 20 0:20 /tenant /sys/cgroup rw - cgroup2 cgroup rw\n',read)
        self.assertFalse(unresolved['limits']);self.assertTrue(unresolved['warnings'])

    def test_cgroup_v1_and_unreadable_limits_do_not_invent_capacity(self):
        files={'/sys/cpu/task/cpu.cfs_quota_us':'50000',
               '/sys/cpu/task/cpu.cfs_period_us':'100000'}
        def read(path):
            if str(path) not in files:raise FileNotFoundError(str(path))
            return files[str(path)]
        mount='30 20 0:20 / /sys/cpu rw - cgroup cgroup rw,cpu,cpuacct\n'
        result=cgroup_cpu_limits('2:cpu,cpuacct:/task\n',mount,read)
        self.assertEqual(result['limits'][0]['capacity_cpus'],.5)
        def denied(path):raise PermissionError('fixture denied')
        result=cgroup_cpu_limits('2:cpu,cpuacct:/task\n',mount,denied)
        self.assertFalse(result['limits']);self.assertTrue(result['warnings'])
        self.assertEqual(parse_cpu_max('max 100000'),(None,100000))
        for text in ('0 100000','100 0','max','-1 100000'):
            with self.assertRaises(ValueError):parse_cpu_max(text)

    def test_worker_measure_and_cost_distinguish_rival_hypotheses(self):
        result=allocation_predictions([1,1,1],[1,8,64],[1,2,4,8])
        self.assertEqual(result['fair_runnable_process_cpu_share'],[1/3]*3)
        self.assertEqual(result['equal_job_service_cpu_share'],[1/73,8/73,64/73])
        changed=allocation_predictions([2,1,0],[1,8,64],[1,2,4,8])
        self.assertEqual(changed['fair_runnable_process_cpu_share'],[2/3,1/3,0])
        self.assertEqual(changed['equal_job_service_cpu_share'],[.2,.8,0])
        self.assertEqual(changed['equal_active_class_cpu_share'],[.5,.5,0])
        self.assertFalse(result['per_thread_and_per_process_identifiable'])

    def test_duty_caps_change_prediction_without_changing_total_capacity(self):
        rates=duty_constrained_rates([.1,1,1],1)
        for actual,expected in zip(rates,[.1,.45,.45]):self.assertAlmostEqual(actual,expected)
        self.assertEqual(duty_constrained_rates([.1,.2],2),[.1,.2])

    def test_direct_cpu_keeps_partial_jobs_and_overhead_in_the_primary_share(self):
        rows=[dict(size=s,completed_jobs=n,cpu_seconds=cpu,
            complete_job_cpu_seconds=work,partial_job_cpu_seconds=partial,
            loop_overhead_cpu_seconds=overhead) for s,n,cpu,work,partial,overhead in
            [(16,2,1.,.6,.3,.1),(32,1,2.,1.5,.4,.1),(64,0,3.,0.,2.9,.1)]]
        result=summarize_trial(rows,[16,32,64],[.25,1.,8.],self.config['log_bin_edges'],[1,1,1])
        self.assertEqual(result['measured_cpu_share_by_class'],[1/6,2/6,3/6])
        self.assertEqual(result['calibrated_completed_job_cpu_by_class'],[.5,1.,0.])
        self.assertEqual(result['partial_job_cpu_seconds_by_class'],[.3,.4,2.9])
        bad=deepcopy(rows);bad[0]['partial_job_cpu_seconds']=0
        with self.assertRaises(ValueError):summarize_trial(bad,[16,32,64],[.25,1.,8.],self.config['log_bin_edges'],[1,1,1])
        bad=deepcopy(rows);bad[0].update(partial_job_cpu_seconds=-.1,loop_overhead_cpu_seconds=.5)
        with self.assertRaises(ValueError):summarize_trial(bad,[16,32,64],[.25,1.,8.],self.config['log_bin_edges'],[1,1,1])

    def test_workload_is_verified_and_deadline_censoring_is_explicit(self):
        result=dense_job(8)
        self.assertTrue(result['completed']);self.assertTrue(result['numerical_valid'])
        self.assertLess(result['relative_residual'],1e-10)
        self.assertEqual(dense_job(8,deadline=0),dict(completed=False,numerical_valid=None))

    def test_conditional_simulation_is_reproducible_and_explicitly_not_observed(self):
        config=dict(self.config,simulation_quanta=100,simulation_replicates=5)
        first=conditional_design(config)
        self.assertEqual(first,conditional_design(config))
        self.assertEqual(first['kind'],'conditional_generated_design_not_scheduler_measurements')
        self.assertIn('not an empirical',first['uncertainty_status'])
        self.assertNotIn('measured_cpu_share_by_class',json.dumps(first))


if __name__=='__main__':unittest.main()
