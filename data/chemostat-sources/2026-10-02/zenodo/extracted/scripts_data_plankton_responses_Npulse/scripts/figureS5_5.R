### LIBRARIES ##################################################################
library(tidyverse)
library(gridExtra)

theme_set(theme_bw())

### LOADING and PREPARING DATA #################################################
df <- read.table("data/plankton_response_avgOEV_TC_share.csv",sep=',',header=TRUE)
df <- df %>% 
  mutate(Treatment=fct_relevel(Treatment,"Bc","Ce","Le","9d","13d"))

### INVESTIGATING DIFFERENCES in RESPONSES MONO- vs POLYCULTURES ###############
# Algal biomass response
anova_BA <- aov(log2(OEV_biovolume_algae) ~ Category, data=df)
summary(anova_BA)
TukeyHSD(anova_BA) # no diff between no herbi and 1 herbi or all herbis but only between 1 and all herbis
# Assumptions verified
plot(density(anova_BA$residuals))
bartlett.test(log2(OEV_biovolume_algae) ~ Category, data=df) 
wilcox.test(log2(OEV_biovolume_algae) ~ Category,data=df)

# Rotifer biomass response
anova_BR <- aov(log2(OEV_biovolume_rotifers) ~ Category, data=df)
summary(anova_BR)
TukeyHSD(anova_BR) # no diff between no herbi and 1 herbi or all herbis but only between 1 and all herbis
# Assumptions verified
plot(density(anova_BR$residuals))
bartlett.test(log2(OEV_biovolume_rotifers) ~ Category, data=df) 
wilcox.test(log2(OEV_biovolume_rotifers) ~ Category,data=df)

# Algal compositional response
anova_CA <- aov(log2(OEV_compo_algae) ~ Category, data=df)
summary(anova_CA)
TukeyHSD(anova_CA) # no diff between no herbi and 1 herbi or all herbis but only between 1 and all herbis
# Assumptions verified
plot(density(anova_CA$residuals))
bartlett.test(log2(OEV_compo_algae) ~ Category, data=df) 
wilcox.test(log2(OEV_compo_algae) ~ Category,data=df)

# Rotifer compositional response 
# > only values for Polycultures so no comparison possible

### PLOTTING ###################################################################
figureS5_5a <- ggplot(data=df,aes(x=Category,y=log2(OEV_biovolume_algae)))+
  geom_boxplot(color=c("steelblue","black"))+
  geom_point(aes(color=Treatment,shape=Treatment),position=position_jitterdodge(seed=42))+
  scale_color_manual("",values=c("Bc"='steelblue','Ce'='steelblue',"Le"="steelblue",
                                 "9d"="black","13d"="black"))+
  scale_shape_manual("",values=c("Bc"=19,'Ce'=8,"Le"=3,"9d"=25,"13d"=17))+
  xlab("")+ylab(bquote(log[2](avgOEV[A])))+
  ylim(-2.5,1.5)+
  ggtitle(paste0("W = ",round(wilcox.test(log2(OEV_biovolume_algae) ~ Category,data=df)$statistic[[1]],2),
                 ", p-value = ", round(wilcox.test(log2(OEV_biovolume_algae) ~ Category,data=df)$p.value,2)))+
  theme(legend.position=c(0.256,0.883),
        legend.margin=margin(c(0.1,0.1,0.1,0.1)),
        legend.box.background = element_rect(colour = "black"),
        text = element_text(size = 13))+
  guides(colour = guide_legend(nrow = 3,title.position ='left'))

figureS5_5b <- ggplot(data=df,aes(x=Category,y=log2(OEV_biovolume_rotifers)))+
  geom_boxplot(color=c("steelblue","black"))+
  geom_point(aes(color=Treatment,shape=Treatment),position=position_jitterdodge(seed=42),
             show.legend=FALSE)+
  scale_color_manual("",values=c("Bc"='steelblue','Ce'='steelblue',"Le"="steelblue",
                                 "9d"="black","13d"="black"))+
  scale_shape_manual("",values=c("Bc"=19,'Ce'=8,"Le"=3,"9d"=25,"13d"=17))+
  xlab("")+ylab(bquote(log[2](avgOEV[R])))+
  ggtitle(paste0("W = ",round(wilcox.test(log2(OEV_biovolume_rotifers) ~ Category,data=df)$statistic[[1]],2),
                 ", p-value = ", round(wilcox.test(log2(OEV_biovolume_rotifers) ~ Category,data=df)$p.value,2)))+
  ylim(-2.5,1.5)+
  theme(text = element_text(size = 13))

figureS5_5c <- ggplot(data=df,aes(x=Category,y=log2(OEV_compo_algae)))+
  geom_boxplot(color=c("steelblue","black"))+
  geom_point(aes(color=Treatment,shape=Treatment),position=position_jitterdodge(seed=42))+
  scale_color_manual("",values=c("Bc"='steelblue','Ce'='steelblue',"Le"="steelblue",
                                 "9d"="black","13d"="black"))+
  scale_shape_manual("",values=c("Bc"=19,'Ce'=8,"Le"=3,"9d"=25,"13d"=17))+
  xlab("")+ylab(bquote(log[2](avgOEV[CA])))+
  ggtitle(paste0("W = ",round(wilcox.test(log2(OEV_compo_algae) ~ Category,data=df)$statistic[[1]],2),
                 ", p-value = ", round(wilcox.test(log2(OEV_compo_algae) ~ Category,data=df)$p.value,2)))+
  theme(legend.position=c(0.256,0.828),
        legend.margin=margin(c(0.1,0.1,0.1,0.1)),
        legend.box.background = element_rect(colour = "black"),
        text = element_text(size = 13))+
  guides(colour = guide_legend(nrow = 3,title.position ='left'))
grid.arrange(grobs=list(figureS5_5a,figureS5_5b),nrow=1)
ggsave("figureS5_5.pdf",
       grid.arrange(grobs=list(figureS5_5a,figureS5_5b),nrow=1),
       path = "./figures", height = 4, width = 6, dpi = 300)

### ADDITIONAL TEST within POLYCULTURES (13d vs 9d) ############################
# Rotifer biovolume response
df_poly <- df %>% filter(Category=="Polycultures")
anova_PolyBR <- aov(log2(OEV_biovolume_rotifers) ~ Treatment, data=df_poly)
summary(anova_PolyBR)
TukeyHSD(anova_PolyBR) # diff between 13d and 9d
# Assumptions verified
plot(density(anova_PolyBR$residuals))
bartlett.test(log2(OEV_biovolume_rotifers) ~ Treatment, data=df_poly) 
wilcox.test(log2(OEV_biovolume_rotifers) ~ Treatment,data=df_poly)
