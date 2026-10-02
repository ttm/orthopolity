# Open the project scripts_data_plankton_responses_Npulse
### LIBRARIES ##################################################################
library(readxl)
library(gridExtra)
library(tidyverse)

### LOADING DATA ###############################################################
data_batch <- read_excel("data/algae_stoichiometry_preliminary_experiments.xlsx")
df_batch <- data.frame(data_batch)

### PLOTTING SETTINGS ##########################################################
# Algae specis: Cr = Cryptomonas sp., Ca = Chlamydomonas reinhardtii,
# Mo = Monoraphidium minutum, Co = Chlorella vulgaris
theme_set(theme_bw())

list_algae <-c("Cr","Ca","Mo","Co") 
colors_algae <-c("#3B528BFF","#00bfff","#35B779FF","#AADC32FF")
lines_algae <-c("dashed","dashed","solid","solid")
points_algae <-rep(19,4)

p1 <-ggplot(df_batch,aes(x=Time.standardised.to.pulse..days.,
                         y=C.N.Ratio..molar.,group=Algae,color=Algae))+
  geom_vline(xintercept=0,colour="black") + # pulse time
  geom_line(aes(linetype=Algae),linewidth=1,show.legend=FALSE)+
  geom_text(aes(x=-4,y=16.5),label="a)",color='black',
            hjust=-0.1,vjust=-1,size=5,show.legend=FALSE)+
  geom_point(aes(shape=Algae),size=4,show.legend=FALSE)+
  scale_colour_manual(name="Algae species",
                      values=c('Cr'=colors_algae[1],
                               'Ca'=colors_algae[2],
                               'Mo'=colors_algae[3],
                               'Co'=colors_algae[4]),
                      breaks=list_algae, labels=list_algae)+
  scale_linetype_manual(name="Algae species",
                        values=c('Cr'=lines_algae[1],
                                 'Ca'=lines_algae[2],
                                 'Mo'=lines_algae[3],
                                 'Co'=lines_algae[4]),
                        breaks=list_algae, labels=list_algae)+
  scale_shape_manual(name="Algae species",
                     values=c('Cr'=points_algae[1],
                              'Ca'=points_algae[2],
                              'Mo'=points_algae[3],
                              'Co'=points_algae[4]),
                     breaks=list_algae, labels=list_algae)+
  xlab("") +
  ylab(expression(paste('C:N ratio (',molar,')',sep='')))+
  theme(text = element_text(size = 13))

p2 <-ggplot(df_batch,aes(x=Time.standardised.to.pulse..days.,
                         y=Density..cells.mL.,group=Algae,color=Algae))+
  geom_vline(xintercept=0,colour="black") + # pulse time
  geom_line(aes(linetype=Algae),linewidth=1,show.legend=FALSE)+
  geom_text(aes(x=-4,y=2e6),label="b)",color='black',
            hjust=-0.1,vjust=-1,size=5,show.legend=FALSE)+
  geom_point(aes(shape=Algae),size=4,show.legend=FALSE)+
  scale_colour_manual(name="Algae",
                      values=c('Cr'=colors_algae[1],
                               'Ca'=colors_algae[2],
                               'Mo'=colors_algae[3],
                               'Co'=colors_algae[4]),
                      breaks=list_algae, labels=list_algae)+
  scale_linetype_manual(name="Algae",
                        values=c('Cr'=lines_algae[1],
                                 'Ca'=lines_algae[2],
                                 'Mo'=lines_algae[3],
                                 'Co'=lines_algae[4]),
                        breaks=list_algae, labels=list_algae)+
  scale_shape_manual(name="Algae",
                     values=c('Cr'=points_algae[1],
                              'Ca'=points_algae[2],
                              'Mo'=points_algae[3],
                              'Co'=points_algae[4]),
                     breaks=list_algae, labels=list_algae)+
  xlab("") +
  ylab(expression(paste('Density (cells.',mL^-1,')',sep=''))) +
  scale_y_continuous(trans='log10',
                     breaks = scales::trans_breaks("log10", function(x) 10^x),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)))+
  theme(text = element_text(size = 13))

p3 <-ggplot(df_batch%>%mutate(Algae=fct_relevel(Algae,"Co","Mo","Ca","Cr")),
            aes(x=Time.standardised.to.pulse..days.,y=Biovolume..µm..mL.,
                group=Algae,color=Algae))+
  geom_vline(xintercept=0,colour="black") + # pulse time
  geom_line(aes(linetype=Algae),linewidth=1)+
  geom_text(aes(x=-4,y=5e7),label="c)",color='black',
            hjust=-0.1,vjust=-1,size=5,show.legend=FALSE)+
  geom_point(aes(shape=Algae),size=4,show.legend=FALSE)+
  scale_colour_manual(name="",
                      values=c('Cr'=colors_algae[1],
                               'Ca'=colors_algae[2],
                               'Mo'=colors_algae[3],
                               'Co'=colors_algae[4]))+
  scale_linetype_manual(name="",
                        values=c('Cr'=lines_algae[1],
                                 'Ca'=lines_algae[2],
                                 'Mo'=lines_algae[3],
                                 'Co'=lines_algae[4]))+
  scale_shape_manual(name="",
                     values=c('Cr'=points_algae[1],
                              'Ca'=points_algae[2],
                              'Mo'=points_algae[3],
                              'Co'=points_algae[4]))+
  scale_y_continuous(trans='log10', 
                     breaks = scales::trans_breaks("log10", function(x) 10^x),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)),
                     limits=c(1.5e7,9e7))+
  xlab("Time standardised to pulse t") +
  ylab(expression(paste('Biovolume (',µm^3,mL^-1,')',sep='')))+
  theme(legend.key.size = unit(1.3,"line"),
        legend.position = c(0.28, 0.889),
        text = element_text(size = 13),
        legend.margin=margin(c(0.1,0.1,0.1,0.1)))+#,
  guides(colour = guide_legend(nrow = 2,title.position ='left'))

p4 <-ggplot(df_batch,aes(x=Time.standardised.to.pulse..days.,
                         y=Cell.volume..µm..,group=Algae,color=Algae))+
  geom_vline(xintercept=0,colour="black") + # pulse time
  geom_line(aes(linetype=Algae),linewidth=1,show.legend=FALSE)+
  geom_text(aes(x=-4,y=150),label="d)",color='black',
            hjust=-0.1,vjust=-1,size=5,show.legend=FALSE)+
  geom_point(aes(shape=Algae),size=4,show.legend=FALSE)+
  scale_colour_manual(name="Algae",
                      values=c('Cr'=colors_algae[1],
                               'Ca'=colors_algae[2],
                               'Mo'=colors_algae[3],
                               'Co'=colors_algae[4]),
                      breaks=list_algae, labels=list_algae)+
  scale_linetype_manual(name="Algae",
                        values=c('Cr'=lines_algae[1],
                                 'Ca'=lines_algae[2],
                                 'Mo'=lines_algae[3],
                                 'Co'=lines_algae[4]),
                        breaks=list_algae, labels=list_algae)+
  scale_shape_manual(name="Algae",
                     values=c('Cr'=points_algae[1],
                              'Ca'=points_algae[2],
                              'Mo'=points_algae[3],
                              'Co'=points_algae[4]),
                     breaks=list_algae, labels=list_algae)+
  xlab("Time standardised to pulse t") +
  ylab(expression(paste('Cell volume (',µm^3,')',sep=''))) +
  scale_y_continuous(trans='log10',
                     breaks = scales::trans_breaks("log10", function(x) 10^x),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)),
                     limits=c(9,320))+
  theme(text = element_text(size = 13))

ggsave("figureS2_2.pdf", grid.arrange(grobs=list(p1,p2,p3,p4),nrow=2), 
       path = "figures/",height = 6, width = 6, dpi = 300)

