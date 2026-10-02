### LIBRARIES ##################################################################
library(readxl)
library(gridExtra)
library(tidyverse)

### LOADING and PREPARING DATA #################################################
## Experimental data
data <- read_excel("data/Chemostat_experimental_timeseries.xlsx")
df <- data.frame(data)

# Relabelling correctly the chemostats and setting correct variable type
WRONG_CHEMOSTATS <- c('1','2','3','4','5','6','7','8','9','10','11','12')
CORRECT_CHEMOSTATS <- c('001','002','003','004','005','006','007','008','009','010','011','012')
for (cs in 1:length(WRONG_CHEMOSTATS)){
  df$Chemostat[df$Chemostat == WRONG_CHEMOSTATS[cs]] <- CORRECT_CHEMOSTATS[cs]
}

df$Category <- as.factor(df$Category)
df$Treatment <- as.factor(df$Treatment)
df$Chemostat <- as.factor(df$Chemostat)
df$Time.standardised.to.pulse <- as.numeric(df$Time.standardised.to.pulse)

for (var in grep("^Biovolume", names(df), value = TRUE)){
  df[var]<-replace(df[var], df[var]==0, NA)}

dfB <-df %>%
  pivot_longer(
    cols = starts_with("Biovolume"),
    names_to = "Organism",
    names_pattern = "Biovolume_?(.*).µm..mL",
    values_to = "Biovolume",
    values_drop_na = TRUE
  ) 

dfB_mono <- dfB %>% filter(Category=="Monocultures", 
                           !Organism %in% c('total_algae','total_rotifers'))
dfB_poly <- dfB %>% filter(Category=="Polycultures", 
                           !Organism %in% c('total_algae','total_rotifers'))

### PLOTTING ###################################################################  
# Plot settings
bk <- c("Monoraphidium_Chlorella","Chlamydomonas","Cryptomonas",
      "Brachionus","Cephalodella","Lecane") # species
lab <- c("Mo+Co","Ca","Cr","Bc","Ce","Le") # corresponding labels in legend

ts_mono <- ggplot(data = dfB_mono %>%
                        mutate(Chemostat=fct_relevel(Chemostat,"Bc1","Ce1","Le1",
                                                     "Bc2","Ce2","Le2","Bc3","Ce3",
                                                     "Le3","Bc4","Ce4","Le4")), 
                      aes(x = Time.standardised.to.pulse)) +
  geom_line(aes(y = Biovolume,color=Organism,linetype=Organism),linewidth=1)+
  geom_point(aes(y = Biovolume,color=Organism,shape=Organism),size=1.5)+
  
  # Settings for colors, linetypes, linewidths and alphas
  scale_colour_manual(name="",
                      values=c('Chlorella'="#AADC32FF",
                               "Monoraphidium"="#35B779FF",
                               "Monoraphidium_Chlorella"="#35B779FF",
                               "Chlamydomonas"="#00bfff",
                               "Cryptomonas"="#3B528BFF",
                               'Brachionus'='firebrick',
                               'Cephalodella'='red',
                               'Lecane'='orange'),
                      breaks=bk, labels=lab)+
  
  scale_linetype_manual(name="",
                        values=c("Chlorella"="dashed",
                                 'Monoraphidium'="dashed",
                                 "Monoraphidium_Chlorella"="dashed",
                                 "Chlamydomonas"="dashed",
                                 "Cryptomonas"="dashed",
                                 'Brachionus'="solid",
                                 'Cephalodella'="solid",
                                 'Lecane'="solid"),                  
                        breaks=bk, labels=lab)+
  
  scale_shape_manual(name="",
                     values=c("Chlorella"=19,
                              'Monoraphidium'=19,
                              "Monoraphidium_Chlorella"=19,
                              "Chlamydomonas"=19,
                              "Cryptomonas"=19,
                              'Brachionus'=1,
                              'Cephalodella'=1,
                              'Lecane'=1),                  
                     breaks=bk, labels=lab)+
  
  geom_vline(xintercept=0,colour="black") + # pulse time
  scale_y_continuous(trans='log10', # log10 y scale and the limits
                     breaks = scales::trans_breaks("log10", function(x) 10^x),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)),
                     limits=c(1e4,5e8))+
  facet_wrap(.~Chemostat,ncol=3) +  # create subplots for  different chemostats
  xlab("Time standardised to day of pulse t") +
  ylab(expression(paste('Biovolume (',µm^3,mL^-1,')',sep=''))) +
  xlim(-6,12)+
  theme_minimal() +
  theme(legend.position="top",text = element_text(size = 16),
        legend.key.size = unit(2,"line"))+
  guides(colour = guide_legend(nrow = 1),linetype = guide_legend(nrow = 1),
         shape = guide_legend(nrow = 1))

ts_poly <- ggplot(data = dfB_poly,aes(x = Time.standardised.to.pulse)) +
  geom_line(aes(y = Biovolume,group=Organism,color=Organism,linetype=Organism),
            linewidth=1)+
  geom_point(aes(y = Biovolume,group=Organism,color=Organism,shape=Organism),size=1.5)+
  
  # Settings for colors, linetypes, linewidths and alphas
  scale_colour_manual(name="",
                      values=c('Chlorella'="#AADC32FF",
                               "Monoraphidium"="#35B779FF",
                               "Monoraphidium_Chlorella"="#35B779FF",
                               "Chlamydomonas"="#00bfff",
                               "Cryptomonas"="#3B528BFF",
                               'Brachionus'='firebrick',
                               'Cephalodella'='red',
                               'Lecane'='orange'),
                      breaks=bk, labels=lab)+
  
  scale_linetype_manual(name="",
                        values=c("Chlorella"="dashed",
                                 'Monoraphidium'="dashed",
                                 "Monoraphidium_Chlorella"="dashed",
                                 "Chlamydomonas"="dashed",
                                 "Cryptomonas"="dashed",
                                 'Brachionus'="solid",
                                 'Cephalodella'="solid",
                                 'Lecane'="solid"),                  
                        breaks=bk, labels=lab)+
  
  scale_shape_manual(name="",
                     values=c("Chlorella"=19,
                              'Monoraphidium'=19,
                              "Monoraphidium_Chlorella"=19,
                              "Chlamydomonas"=19,
                              "Cryptomonas"=19,
                              'Brachionus'=1,
                              'Cephalodella'=1,
                              'Lecane'=1),                  
                     breaks=bk, labels=lab)+
  
  geom_vline(xintercept=0,colour="black") + # pulse time
  scale_y_continuous(trans='log10', # log10 y scale and the limits
                     breaks = scales::trans_breaks("log10", function(x) 10^x),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)),
                     limits=c(1e4,5e8))+#,
  facet_wrap(.~Chemostat,ncol=3,
             labeller=labeller(Chemostat=c("001"="001 (13d)","002"="002 (13d)",
                                           "003"="003 (9d)","004"="004 (9d)",
                                           "005"="005 (13d)","006"="006 (9d)",
                                           "007"="007 (13d)","008"="008 (13d)",
                                           "009"="009 (13d)","010"="010 (9d)",
                                           "011"="011 (9d)","012"="012 (9d)"))) +  # create subplots for  different chemostats
  xlab("Time standardised to day of pulse t") +
  ylab(expression(paste('Biovolume (',µm^3,mL^-1,')',sep=''))) +
  xlim(-6,12)+
  theme_minimal() +
  theme(legend.position="top",text = element_text(size = 16),
        legend.key.size = unit(2,"line"))+#,
  guides(colour = guide_legend(nrow = 1),linetype = guide_legend(nrow = 1),
         shape = guide_legend(nrow = 1))

# save plots
ggsave("figureS4_1.pdf",ts_mono,
       path = "figures/",height = 10, width = 8, dpi = 300)
ggsave("figureS4_2.pdf",ts_poly,
       path = "figures/",height = 10, width = 8, dpi = 300)
