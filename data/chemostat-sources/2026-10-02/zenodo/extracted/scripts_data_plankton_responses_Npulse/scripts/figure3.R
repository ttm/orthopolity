# Open the project scripts_data_plankton_responses_Npulse
### LIBRARIES ##################################################################
library(readxl)
library(gridExtra)
library(tidyverse)

### LOADING and PREPARING DATA #################################################
## Experimental data
data <- read_excel("data/Chemostat_experimental_timeseries.xlsx")
df <- data.frame(data)

## Bayesian predictions for monocultures and polycultures
pred_mono <- read.csv("data/bayesian_predictions_monocultures.csv",sep=",",header=TRUE)
pred_poly <- read.csv("data/bayesian_predictions_polycultures.csv",sep=",",header=TRUE)
pred <- rbind(pred_mono,pred_poly)

# Relabelling correctly the chemostats and setting correct variable type
WRONG_CHEMOSTATS <- c('1','2','3','4','5','6','7','8','9','10','11','12')
CORRECT_CHEMOSTATS <- c('001','002','003','004','005','006','007','008','009','010','011','012')
for (cs in 1:length(WRONG_CHEMOSTATS)){
  df$Chemostat[df$Chemostat == WRONG_CHEMOSTATS[cs]] <- CORRECT_CHEMOSTATS[cs]
  pred$Chemostat[pred$Chemostat == WRONG_CHEMOSTATS[cs]] <- CORRECT_CHEMOSTATS[cs]
}

df$Category <- as.factor(df$Category)
df$Treatment <- as.factor(df$Treatment)
df$Chemostat <- as.factor(df$Chemostat)
pred$Chemostat <- as.factor(pred$Chemostat)
df$Time.standardised.to.pulse <- as.numeric(df$Time.standardised.to.pulse)

factor = 1e6 # link between scale biovolume and nitrogen

## Preparing the datasets for plotting
pred <- merge(df[,1:3],pred,by='Chemostat')%>%
  filter(Time.standardised.to.pulse>=-6,Time.standardised.to.pulse<=12)

for (var in grep("^Biovolume", names(df), value = TRUE)){
  df[var]<-replace(df[var], df[var]==0, NA)}

dfB <-df %>% rowwise() %>%
  mutate(Biovolume_Algae.µm..mL = rowSums(pick(Biovolume_Cryptomonas.µm..mL:Biovolume_Monoraphidium_Chlorella.µm..mL),
                                          na.rm=TRUE),
         Biovolume_Rotifers.µm..mL = rowSums(pick(Biovolume_Brachionus.µm..mL:Biovolume_Lecane.µm..mL),
                                             na.rm=TRUE)) %>%
  pivot_longer(
    cols = starts_with("Biovolume"),
    names_to = "Organism",
    names_pattern = "Biovolume_?(.*).µm..mL",
    values_to = "Biovolume",
    values_drop_na = TRUE
  ) 

predB_Q1 <- pred[,c(1:5,8,11)] 
colnames(predB_Q1)[5:7] <- c("Nitrogen.Q1","Algae.Q1","Rotifers.Q1")
predB_Q1 <- predB_Q1 %>%
  mutate(Nitrogen.Q1 = Nitrogen.Q1*factor)%>%
  pivot_longer(
    cols = ends_with("Q1"), names_pattern="(.*).Q1",
    names_to = "Organism",values_to = "Q1",values_drop_na = FALSE)

predB_Q2 <- pred[,c(1:4,6,9,12)]
colnames(predB_Q2)[5:7] <- c("Nitrogen.Q2","Algae.Q2","Rotifers.Q2")
predB_Q2 <- predB_Q2 %>%
  mutate(Nitrogen.Q2 = Nitrogen.Q2*factor)%>%
  pivot_longer(
    cols = ends_with("Q2"),names_pattern="(.*).Q2",
    names_to = "Organism",values_to = "Q2",values_drop_na = FALSE)

predB_Q3 <- pred[,c(1:4,7,10,13)]
colnames(predB_Q3)[5:7] <- c("Nitrogen.Q3","Algae.Q3","Rotifers.Q3")
predB_Q3 <- predB_Q3 %>%
  mutate(Nitrogen.Q3 = Nitrogen.Q3*factor)%>%
  pivot_longer(
    cols=ends_with("Q3"),names_pattern="(.*).Q3",
    names_to = "Organism",values_to = "Q3",values_drop_na = FALSE)

predB <- predB_Q1 %>% mutate(Q2=predB_Q2$Q2, Q3=predB_Q3$Q3)

dfpredB <- merge(dfB,predB,by=c("Chemostat","Category","Treatment",
                                "Time.standardised.to.pulse",
                                "Organism"),all = TRUE)

### PLOTTING ###################################################################
## Plotting settings
selectedCS <- c('Bc3','Bc4','Ce1','Le4','002','011','012','009')
labels_CS <- c("Bc3"="Monoculture TC=3.34","Bc4"="Monoculture TC=1.85",
               "Ce1"="Monoculture TC=0.66","Le4"="Monoculture TC=0.13",
               "002"="Polyculture TC=0.65","011"="Polyculture TC=1.94",
               "012"="Polyculture TC=2.83", "009"="Polyculture TC=3.25")
dat_text <- data.frame(label = c("d)", "c)", "b)","a)","e)","f)","g)","h)"),
                       Chemostat = selectedCS)%>%
  mutate(Chemostat=fct_relevel(Chemostat,'Le4','002','Ce1','011','Bc4',
                               '012','Bc3','009'))
## Selecting some experimental timeseries
dfpredB_selectedCS <- dfpredB %>%
  filter(Chemostat %in% selectedCS,
         Organism %in% c('Nitrogen','Algae','Rotifers'))%>%
  mutate(Chemostat=fct_relevel(Chemostat,'Le4','002','Ce1','011','Bc4','012',
                               'Bc3','009'))

figure3 <- ggplot() +
  geom_text(data=dat_text,aes(x=-5,y=1e8,label=label),
            hjust=-0.1,vjust=-1,size=5)+
  geom_ribbon(data=dfpredB_selectedCS %>% filter(!is.na(Q1)),
              aes(x = Time.standardised.to.pulse,ymin=Q1,
                  ymax=Q3,group=Organism,fill=Organism),alpha=0.2)+
  geom_line(data=dfpredB_selectedCS %>% filter(!is.na(Q2)),
            aes(x = Time.standardised.to.pulse,y=Q2,group=Organism,
                color=Organism,linetype=Organism),linewidth=1)+ # plot lines 
  geom_point(data=dfpredB_selectedCS %>% filter(!is.na(Biovolume)),
             aes(x = Time.standardised.to.pulse,y = Biovolume,
                 group=Organism,color=Organism,shape=Organism),size=2)+
  
  # Settings for colors, linetypes, linewidths and alphas
  scale_colour_manual(name="", values=c('Nitrogen'='grey50','Algae'="#AADC32FF", "Rotifers"="magenta"))+
  scale_fill_manual(name="", values=c('Nitrogen'='grey50','Algae'="#AADC32FF","Rotifers"="magenta"))+  
  scale_shape_manual(name="", values=c('Nitrogen'=1,'Algae'=19,'Rotifers'=1))+
  scale_linetype_manual(name="", values=c('Nitrogen'='dotted','Algae'='dashed','Rotifers'='solid'))+
  
  geom_vline(xintercept=0,colour="black") + # pulse time
  scale_y_continuous(trans='log10', # log10 y scale and the limits
                     breaks = scales::trans_breaks("log10", function(x) 10^x),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)),
                     limits=c(6e4,6e8),
                     sec.axis = sec_axis(transform = ~ . * 1/ factor,
                                         breaks = scales::trans_breaks("log10", function(x) 10^x),
                                         labels = scales::trans_format("log10", scales::math_format(10^.x)),
                                         name = expression(paste('Nitrogen concentration (',µmol,' N ',L^-1,')',sep='')))) + 
  
  facet_wrap(.~Chemostat,ncol=2,labeller=labeller(Chemostat=labels_CS)) +  
  # create subplots for  different chemostats
  xlab("Time standardised to pulse t \n") +
  ylab(expression(paste('Biovolume (',µm^3,mL^-1,')',sep=''))) +
  xlim(-6,12)+
  theme_minimal() +
  theme(legend.position=c(0.5,-0.14),text = element_text(size = 14),
        legend.text=element_text(size=14),
        legend.key.size = unit(1.2,"line"),strip.text = element_text(size = 14),
        axis.text.y.right = element_text(color = "grey50"),
        axis.title.y.right = element_text(color = "grey50",face = "bold"))+
  guides(colour = guide_legend(nrow = 1),shape = guide_legend(nrow = 1),
         fill = guide_legend(nrow = 1),linetype = guide_legend(nrow = 1))

# save figure 3 in the figures folder
ggsave("figure3.pdf",figure3,
       path = "figures/",height = 7, width = 7, dpi = 300)

