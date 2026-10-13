% Plot file
%
% A. Fontana & L. Bellon - 02/23

%% PLOTS C100

%% Flexural modes
c = linspecer(8);
lnw = 0.75;
mks = 3;
figure
fon = figuresize2_2rows();
ha = tight_subplot(2,1,[.1 0.08],[.09 .05],[.15 .05]);
axes(ha(1));
for idx = [2:4 6:8]
    errorbar(C100.AVG_TAVG,C100.AVG_D_TFLUC(:,idx),C100.AVG_D_TFLUC_ERR(:,idx),C100.AVG_D_TFLUC_ERR(:,idx),...
        C100.AVG_TAVG_ERR,C100.AVG_TAVG_ERR,'o-','Color',c(idx,:),'DisplayName',['$n=$ ' num2str(idx)],...
        'LineWidth',lnw,'MarkerSize',mks)
    hold on
end
plot(C100.AVG_TAVG,C100.AVG_TAVG,'k','DisplayName','$T^\mathrm{avg}$','LineWidth',lnw)
plot(C100.AVG_TAVG,C100.AVG_TMAX,'k--','DisplayName','$T^\mathrm{max}$','LineWidth',lnw)
temp = 300:max(C100.AVG_TAVG)*1.1;
plot(temp,300*temp./temp,'k:','DisplayName','$T^\mathrm{min}$','LineWidth',lnw)
xlim([300 700])
ylim([200 650])
xticks([200:100:700])
yticks([200:100:700])
labellatex('Average $T^\mathrm{avg}$ [K]','Flexural $T^\mathrm{fluc}_n$ [K]',fon)
legendlatex(fon-3,'northwest',20,2)
text(.93,0.93,'(a)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

axes(ha(2));
for idx = [2:4 6:8]
    errorbar(C100.AVG_TAVG,C100.AVG_D_PHI(:,idx),C100.AVG_D_PHI_ERR(:,idx),C100.AVG_D_PHI_ERR(:,idx),...
        C100.AVG_TAVG_ERR,C100.AVG_TAVG_ERR,'o-','Color',c(idx,:),'DisplayName',['$n=$ ' num2str(idx)],...
        'LineWidth',lnw,'MarkerSize',mks)
    hold on
end
xlim([300 700])
ylim([0e-5 4.5e-5])
xticks([200:100:700])
labellatex('Average $T^\mathrm{avg}$ [K]','Flexural $\varphi_n$',fon)
text(.93,0.93,'(b)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

%% Torsional modes
c = linspecer(8);
lnw = 0.75;
figure
fon = figuresize2_2rows();
ha = tight_subplot(2,1,[.1 0.08],[.09 .05],[.15 .05]);
axes(ha(1));
for idx = [1:4 6:8]
    errorbar(C100.AVG_TAVG,C100.AVG_T_TFLUC(:,idx),C100.AVG_T_TFLUC_ERR(:,idx),C100.AVG_T_TFLUC_ERR(:,idx),...
        C100.AVG_TAVG_ERR,C100.AVG_TAVG_ERR,'o-','Color',c(idx,:),'DisplayName',['$m=$ ' num2str(idx)],...
        'LineWidth',lnw,'MarkerSize',mks)
    hold on
end
plot(C100.AVG_TAVG,C100.AVG_TAVG,'k','DisplayName','$T^\mathrm{avg}$','LineWidth',lnw)
plot(C100.AVG_TAVG,C100.AVG_TMAX,'k--','DisplayName','$T^\mathrm{max}$','LineWidth',lnw)
temp = 300:max(C100.AVG_TAVG)*1.1;
plot(temp,300*temp./temp,'k:','DisplayName','$T^\mathrm{min}$','LineWidth',lnw)
xlim([300 700])
ylim([200 650])
xticks([200:100:700])
yticks([200:100:700])
labellatex('Average $T^\mathrm{avg}$ [K]','Torsional $T^\mathrm{fluc}_m$ [K]',fon)
legendlatex(fon-3,'northwest',20,2)
text(.93,0.93,'(a)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

axes(ha(2));
for idx = [1:4 6:8]
    errorbar(C100.AVG_TAVG,C100.AVG_T_PHI(:,idx),C100.AVG_T_PHI_ERR(:,idx),C100.AVG_T_PHI_ERR(:,idx),...
        C100.AVG_TAVG_ERR,C100.AVG_TAVG_ERR,'o-','Color',c(idx,:),'DisplayName',['$n=$ ' num2str(idx)],...
        'LineWidth',lnw,'MarkerSize',mks)
    hold on
end
xlim([300 700])
ylim([0e-5 3.5e-5])
xticks([200:100:700])
labellatex('Average $T^\mathrm{avg}$ [K]','Torsional $\varphi_m$',fon)
text(.93,0.93,'(b)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

%% PLOTS C30

%% Flexural modes (not 3)
c = linspecer(8);
figure
fon = figuresize2_2rows();
ha = tight_subplot(2,2,[.1 0.15],[.09 .02],[.15 .05]);
idx = 1;
lnw = 0.75;
mks = 3;
txt = {'(b)','(c)','(d)','(e)'};
limy = [700 700 700 700];
for idxm=[1 2 4 5]
    axes(ha(idx));
    errorbar(C30.AVG_TAVG,C30.AVG_D_TFLUC(:,idxm),C30.AVG_D_TFLUC_ERR(:,idxm),...
        C30.AVG_D_TFLUC_ERR(:,idxm),C30.AVG_TAVG_ERR,...
        C30.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'LineWidth',lnw,'MarkerSize',mks,...
        'DisplayName',['$n=$ ' num2str(idxm)])
    hold on
    plot(C30.AVG_TAVG,C30.AVG_TAVG,'k-','LineWidth',lnw,'DisplayName','$T^\mathrm{avg}$')
    plot(C30.AVG_TAVG,C30.AVG_TMAX,'k--','DisplayName','$T^\mathrm{max}$','LineWidth',lnw)

    plot(C30.AVG_D_TAVG,C30.AVG_D_TTHEO(:,idxm),'k:','LineWidth',lnw,...
        'DisplayName','$T^\mathrm{theo}$')
    xlim([300 600])
    ylim([250 limy(idx)])
    labellatex('Average $T^\mathrm{avg}$ [K]',['Flexural $T^\mathrm{fluc}_' num2str(idxm) '$ [K]'],fon)
    legendlatex(fon-3,'northwest',20)
    text(.84,0.05,txt{idx},'Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');
    idx = idx+1;
end

%% Flexural mode 3
figure;
fon = figuresize2();
ha = tight_subplot(1,2,[.1 0.15],[.18 .08],[.15 .05]);
idxm = 3;
axes(ha(1));
errorbar(C30.AVG_TAVG,C30.AVG_D_TFLUC(:,idxm),C30.AVG_D_TFLUC_ERR(:,idxm),...
    C30.AVG_D_TFLUC_ERR(:,idxm),C30.AVG_TAVG_ERR,...
    C30.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'LineWidth',lnw,...
    'DisplayName',['$n=$ ' num2str(idxm)],'MarkerSize',mks)
hold on
plot(C30.AVG_TAVG,C30.AVG_TAVG,'k-','LineWidth',lnw,'DisplayName','$T^\mathrm{avg}$')
plot(C30.AVG_TAVG,C30.AVG_TMAX,'k--','DisplayName','$T^\mathrm{max}$','LineWidth',lnw)

plot(C30.AVG_D_TAVG,C30.AVG_D_TTHEO(:,idxm),'k:','LineWidth',lnw,...
    'DisplayName','$T^\mathrm{theo}$')
xlim([300 600])
ylim([250 600])
labellatex('Average $T^\mathrm{avg}$ [K]','Flexural $T^\mathrm{fluc}_3$ [K]',fon)
legendlatex(fon-3,'northwest',20)
text(.84,0.05,'(a)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

axes(ha(2));
errorbar(C30.AVG_TAVG,C30.AVG_D_PHI(:,idxm),C30.AVG_D_PHI_ERR(:,idxm),C30.AVG_D_PHI_ERR(:,idxm),...
    C30.AVG_TAVG_ERR,C30.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'DisplayName',['$n=$ ' num2str(idxm)],...
    'LineWidth',lnw,'MarkerSize',mks)
labellatex('Average $T^\mathrm{avg}$ [K]','Flexural $\varphi_3$',fon)
legendlatex(fon-3,'northwest',20)
text(.84,0.05,'(b)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

%% Flexural dissipation
figure
fon = figuresize2();
ha = tight_subplot(1,1,[.1 0.15],[.18 .08],[.15 .05]);
axes(ha(1))
for idx=[1 2 3 4 5]
    errorbar(C30.AVG_TAVG,C30.AVG_D_PHI(:,idx),C30.AVG_D_PHI_ERR(:,idx),C30.AVG_D_PHI_ERR(:,idx),...
        C30.AVG_TAVG_ERR,C30.AVG_TAVG_ERR,'o-','Color',c(idx,:),'DisplayName',['$n=$ ' num2str(idx)],...
        'LineWidth',lnw,'MarkerSize',mks)
    hold on
end
labellatex('Average $T^\mathrm{avg}$ [K]','Flexural $\varphi_n$',fon)
legendlatex(fon-3,'northwest',20)
ylim([0 1.2e-4])
yticks(0:0.4e-4:1.2e-4)
text(.93,0.93,'(a)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

%% Torsional plot
figure
fon = figuresize2();
ha = tight_subplot(1,2,[.1 0.15],[.16 .08],[.15 .05]);
axes(ha(1))
idxm=1;
errorbar(C30.AVG_TAVG,C30.AVG_T_TFLUC(:,idxm),C30.AVG_T_TFLUC_ERR(:,idxm),...
    C30.AVG_T_TFLUC_ERR(:,idxm),C30.AVG_TAVG_ERR,...
    C30.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'LineWidth',lnw,...
    'DisplayName',['$m=$ ' num2str(idxm)],'MarkerSize',mks)
hold on    
plot(C30.AVG_TAVG,C30.AVG_TAVG,'k-','LineWidth',lnw,'DisplayName','$T^\mathrm{avg}$')
plot(C30.AVG_TAVG,C30.AVG_TMAX,'k--','DisplayName','$T^\mathrm{max}$','LineWidth',lnw)
plot(C30.AVG_T_TAVG,C30.AVG_T_TTHEO(:,idxm),'k:','LineWidth',lnw,...
    'DisplayName','$T^\mathrm{theo}$')
xlim([300 600])
ylim([250 600])
labellatex('Average $T^\mathrm{avg}$ [K]','Torsional $T^\mathrm{fluc}_1$ [K]',fon)
legendlatex(fon-3,'northwest',20)
text(.84,0.05,'(a)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

axes(ha(2))
errorbar(C30.AVG_TAVG,C30.AVG_T_PHI(:,idxm),C30.AVG_T_PHI_ERR(:,idxm),C30.AVG_T_PHI_ERR(:,idxm),...
    C30.AVG_TAVG_ERR,C30.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'DisplayName',['$m=$ ' num2str(idxm)],...
    'LineWidth',lnw,'MarkerSize',mks)
labellatex('Average $T^\mathrm{avg}$ [K]','Torsional $\varphi_1$',fon)
legendlatex(fon-3,'northwest',20)
text(.84,0.05,'(b)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

%% C30C

%% Flexural modes

c = linspecer(8);
figure
fon = figuresize2_2rows();
ha = tight_subplot(2,2,[.1 0.15],[.09 .02],[.15 .05]);
idx = 1;
lnw = 0.75;
txt = {'(b)','(c)','(d)','(e)'};
legpos = {'northeast','southeast','southeast','southeast'};
txtpos = [ .03, .93; .03, .93; .03, .93; .03, .93];
limy = [550 550 550 550];
limy2 = [250 250 250 250];
for idxm=[1 2 3 4]
    axes(ha(idx));
    errorbar(C30C.AVG_TAVG,C30C.AVG_D_TFLUC(:,idx),C30C.AVG_D_TFLUC_ERR(:,idx),C30C.AVG_D_TFLUC_ERR(:,idx),...
        C30C.AVG_TAVG_ERR,C30C.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'LineWidth',lnw,...
        'DisplayName',['$n=$ ' num2str(idxm)],'MarkerSize',mks)
    hold on   
    plot(C30C.AVG_TAVG,C30C.AVG_TAVG,'k-','LineWidth',lnw,'DisplayName','$T^\mathrm{avg}$')
    plot(C30C.AVG_TAVG,C30C.AVG_TMAX,'k--','DisplayName','$T^\mathrm{max}$','LineWidth',lnw)
    plot(C30C.AVG_D_TAVG,C30C.AVG_D_TTHEO(:,idxm),'k:','LineWidth',lnw,...
        'DisplayName','$T^\mathrm{theo}$')
    xlim([300 500])
    ylim([limy2(idx) limy(idx)])
    labellatex('Average $T^\mathrm{avg}$ [K]',['Flexural $T^\mathrm{fluc}_' num2str(idxm) '$ [K]'],fon)
    legendlatex(fon-3,legpos{idx},20)
    text(txtpos(idx,1),txtpos(idx,2),txt{idx},'Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');
    idx = idx+1;
end

%% Flexural dissipation
figure
fon = figuresize2();
ha = tight_subplot(1,1,[.1 0.15],[.18 .08],[.15 .05]);
axes(ha(1));
C30C.AVG_D_PHI(1,4) = NaN;
for idx=1:4
    errorbar(C30C.AVG_TAVG,C30C.AVG_D_PHI(:,idx),C30C.AVG_D_PHI_ERR(:,idx),C30C.AVG_D_PHI_ERR(:,idx),...
        C30C.AVG_TAVG_ERR,C30C.AVG_TAVG_ERR,'o-','Color',c(idx,:),'DisplayName',['$n=$ ' num2str(idx)],...
        'LineWidth',lnw,'MarkerSize',mks)
    hold on
end
labellatex('Average $T^\mathrm{avg}$ [K]','Flexural $\varphi_n$',fon)
legendlatex(fon-3,'northwest',20)
ylim([2e-4 8e-4])
yticks(0:2e-4:1e-3)
box on
text(.93,0.05,'(a)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

%% Torsional plot
C30C.AVG_T_PHI(1:3,2)=NaN;
figure
fon = figuresize2();
ha = tight_subplot(1,2,[.1 0.15],[.17 .08],[.15 .05]);
axes(ha(1))
for idxm=1
    errorbar(C30C.AVG_TAVG,C30C.AVG_T_TFLUC(:,idxm),C30C.AVG_T_TFLUC_ERR(:,idxm),...
        C30C.AVG_T_TFLUC_ERR(:,idxm),C30C.AVG_TAVG_ERR,...
        C30C.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'LineWidth',lnw,...
        'DisplayName',['$m=$ ' num2str(idxm)],'MarkerSize',mks)
    hold on
end
dt = 0:400;
tavg = 300 + dt/2;
tmax = 300 + dt;
plot(tavg,tavg,'k-','LineWidth',lnw,'DisplayName','$T^\mathrm{avg}$')
plot(tavg,tmax,'k--','DisplayName','$T^\mathrm{max}$','LineWidth',lnw)
for idxm=1
    plot(C30C.AVG_T_TAVG,C30C.AVG_T_TTHEO(:,idxm),'k:','LineWidth',lnw,...
        'DisplayName','$T^\mathrm{theo}$')
end
xlim([300 500])
ylim([300 550])
labellatex('Average $T^\mathrm{avg}$ [K]','Torsional $T^\mathrm{fluc}_1$ [K]',fon)
legendlatex(fon-3,'northwest',20)
text(.84,0.05,'(a)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');

axes(ha(2))
for idxm=1
    errorbar(C30C.AVG_TAVG,C30C.AVG_T_PHI(:,idxm),C30C.AVG_T_PHI_ERR(:,idxm),C30C.AVG_T_PHI_ERR(:,idxm),...
        C30C.AVG_TAVG_ERR,C30C.AVG_TAVG_ERR,'o-','Color',c(idxm,:),'DisplayName',['$m=$ ' num2str(idxm)],...
        'LineWidth',lnw,'MarkerSize',mks)
    hold on
end
ylim([4 6]*1e-4)
labellatex('Average $T^\mathrm{avg}$ [K]','Torsional $\varphi_1$',fon)
legendlatex(fon-3,'northwest',20)
text(.84,0.05,'(b)','Units','Normalized','Interpreter','latex','FontSize',fon,'Color','k');