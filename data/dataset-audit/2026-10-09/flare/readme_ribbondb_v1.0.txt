------------------------------------------------------------------------------------------------
                                    RIBBONDB README FILE
------------------------------------------------------------------------------------------------
This is the first release of the flare ribbon catalogue RibbonDB or RibbonDB_V1.0 from 31 March 2017,
described in Kazachenko et al. 2017 (Table 2) contains properties of active region and flare ribbons 
for all flares of GOES class  C1.0 and larger observed in the SDO era, from April 2010 until 
April 2016, 3137 events total. 

To select the events for our flare ribbon catalogue we used the existing Heliophysics Event Catalogue (HEC) 
maintained by the INAF-Trieste Astronomical Observatory which contains information 
of flares from various instruments. To avoid projection effects, we selected only the 
flare events with heliographic longitudes less than 45 degrees. We also excluded 
events with a missing active region number. For active regions with missing 
coordinates, we used get_nar.pro from SolarSoft to obtain the AR location coordinates. 

As a result we derived a selection of 3137 flares for RibbonDB catalogue, including 17 X-class, 
250 M-class, and 2870 C-class flares. 

Each entry in RibbonDB contains the following information from HEC: 
    TSTART - flare start time  [UT]
    TPEAK - flare time of peak X-ray flux [UT]
    TFINAL - flare end time [UT]
    IXPEAK -  peak 1-8A X-ray flux [W/M^2]
    LON - flare heliographic longitude [DEG]
    LAT -  lare heliographic latitude [DEG]
    ARNUM - active region number [].

For each event in the database we use AIA 1600A image sequence, of 24-seconds cadence and 
0.61\arcsec  spatial resolution, and a pre-flare HMI vector field magnetogram, of 12-minutes 
cadence and 0.5 arcsec spatial resolution, to derive the flare-ribbon-pixel masks and the 
radial (normal) component of the magnetic field, B_n, accordingly. We used these 
observations to compute the following large-scale, event- and area-integrated quantities: 

    PHI_AR - total unsigned active region magnetic flux  [MX]
    PHI_RBN - total unsigned flare-ribbon reconnection flux [MX]
    DPHI_RBN - flare-ribbon reconnection flux uncertainty derived by varying ribbon cutout threshold [MX]
    S_AR - active region area  [CM^2]
    S_RBN - flare ribbon area [CM^2]
    DS_RBN - flare ribbon area uncertainty [CM^2]
    R_PHI - ratio between reconnected magnetic flux and AR magnetic flux [%]
    R_S - ratio between ribbon area and AR area [%]

To derive signed reconnection flux from unsigned quantity: 
                PHI_REC=PHI_RBN/2,
                DPHI_REC=DPHI_RBN/2.

To restore IDL sav file ribbonDB_v1.0.sav you would need IDL. Here are several commands that will help:
    >IDL  restore,'ribbondb_v1.0.sav'
    >IDL  help, ribbondb,/st 
    >IDL  plot,ribbondb.phi_rbn,ribbondb.ixpeak,/xlog,/ylog,psym=2

If you don't have IDL, please use ribbonDB_v1.0.csv text file.

----------------------------------------------------------------------------------
For questions please email Maria D. Kazachenko: kazachenko@ssl.berkeley.edu
31 March 2017
UC Berkeley
Space Sciences Laboratory 

------------------------------------------------------------------------------------------------
