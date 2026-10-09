# Open the project scripts_data_plankton_responses_Npulse
### LIBRARIES ##################################################################
library(readxl)
library(gridExtra)
library(tidyverse)

### LOADING and PREPARING DATA #################################################
## Experimental data
data <- read_excel("data/algae_no-rotifer_chemostat_preliminary_experiments.xlsx")
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

### PLOTTING ###################################################################
bk <- c("Chlorella", "Monoraphidium","Monoraphidium_Chlorella",
         "Chlamydomonas","Cryptomonas") 
lab <- c("Co","Mo","Mo+Co","Ca","Cr") # name columns in dataset

figureS2_1 <- ggplot(data = dfB %>%
                   filter(!Organism %in% c('total_algae','total_rotifers')) %>%
                   mutate(Organism=case_when(Treatment=='Co'~'Chlorella',
                                             Treatment=='Mo'~'Monoraphidium',
                                             .default=Organism),
                          Chemostat = substr(Chemostat,3,3),
                          Treatment=fct_relevel(Treatment,"Co","Mo","Ca","Cr","Mi")), 
                 aes(x = Time.standardised.to.pulse,y = Biovolume,color=Organism)) +
  geom_line(aes(linetype=Chemostat),linewidth=0.5)+#Organism))+ # plot lines 
  geom_point(aes(shape=Organism),size=1.5)+
  
  # Settings for colors, linetypes, linewidths and alphas
  scale_colour_manual(name="",
                      values=c("Chlorella"="#AADC32FF",
                               "Monoraphidium"="#35B779FF",
                               "Monoraphidium_Chlorella"="#35B779FF",
                               "Chlamydomonas"="#00bfff",
                               "Cryptomonas"="#3B528BFF"),
                      breaks=bk, labels=lab)+
  scale_shape_manual(name="",
                     values=c("Chlorella"=19,
                              "Monoraphidium"=19,
                              "Monoraphidium_Chlorella"=3,
                              "Chlamydomonas"=19,
                              "Cryptomonas"=19),                  
                     breaks=bk, labels=lab)+
  scale_linetype_manual(name="",values=c("1"="solid","2"="dashed"))+
  geom_vline(xintercept=0,colour="black") + # pulse time
  scale_y_continuous(trans='log10',
                     breaks = scales::trans_breaks("log10", function(x) 10^x),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)),
                     limits=c(2.2e6,1.2e8)) + # log10 y scale and the limits
  facet_wrap(.~Treatment,ncol=2,
             labeller=labeller(Treatment=c("Co"="C. vulgaris",
                                           "Mo"="M. minutum",
                                           "Ca"="C.reinhardtii",
                                           "Cr"="Cryptomonas sp.",
                                           "Mi"="Algae polyculture"))) + 
  xlab("Time standardised to pulse t") +
  ylab(expression(paste('Biovolume (',µm^3,mL^-1,')',sep=''))) +
  xlim(-6,12)+
  theme_minimal() +
  theme(legend.position=c(0.8,0.15),text = element_text(size = 14))+
  guides(colour = guide_legend(nrow = 3),shape = guide_legend(nrow = 3),
         linetype="none")

ggsave("figureS2_1.pdf",figureS2_1,
       path = "figures/",height = 6, width = 6, dpi = 300)


