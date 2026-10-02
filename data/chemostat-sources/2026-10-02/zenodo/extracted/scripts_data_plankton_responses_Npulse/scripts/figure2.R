# Open the project scripts_data_plankton_responses_Npulse
### LIBRARIES ##################################################################
library(tidyverse)
library(gridExtra)
library(vegan)
library(brms)

theme_set(theme_bw())

### LOADING and PREPARING DATA #################################################
df <- read.table("data/plankton_response_avgOEV_TC_share.csv",sep=',',header=TRUE)
df <- df %>% 
  mutate(Treatment=fct_relevel(Treatment,"Bc","Ce","Le","9d","13d"))

### INVESTIGATING the BIOMASS RESPONSES ########################################
### Algal responses
## Quadratic regressions
fit.A.sep = brm(log2(OEV_biovolume_algae) ~ (TC_at_pulse+I(TC_at_pulse^2))*Category,
                data = df)
fit.A.all = brm(log2(OEV_biovolume_algae) ~ (TC_at_pulse+I(TC_at_pulse^2)),
                data = df)

pred.A.sep = conditional_effects(fit.A.sep,effects = "TC_at_pulse:Category",prob = 0.95)
pred.A.all = conditional_effects(fit.A.all,effects = "TC_at_pulse",prob = 0.95)

df_pred.A.sep = data.frame(cbind(pred.A.sep$`TC_at_pulse:Category`$effect2__,
                                 pred.A.sep$`TC_at_pulse:Category`$effect1__,
                                 pred.A.sep$`TC_at_pulse:Category`$estimate__,
                                 pred.A.sep$`TC_at_pulse:Category`$lower__,
                                 pred.A.sep$`TC_at_pulse:Category`$upper__))
names(df_pred.A.sep) <- c("Category","TC_at_pulse","Estimate","Lower","Upper")

df_pred.A.all = data.frame(cbind(pred.A.all$`TC_at_pulse`$effect1__,
                                 pred.A.all$`TC_at_pulse`$estimate__,
                                 pred.A.all$`TC_at_pulse`$lower__,
                                 pred.A.all$`TC_at_pulse`$upper__))
names(df_pred.A.all) <- c("TC_at_pulse","Estimate","Lower","Upper")

## Quadratic effects
# monocultures
hypothesis(fit.A.sep, "ITC_at_pulseE2<0") 
# polycultures
hypothesis(fit.A.sep, "ITC_at_pulseE2+(ITC_at_pulseE2:CategoryPolycultures)<0") 
# all
hypothesis(fit.A.all, "ITC_at_pulseE2<0")

### Rotifer responses
## Quadratic regressions
fit.R.sep = brm(log2(OEV_biovolume_rotifers) ~ (TC_at_pulse+I(TC_at_pulse^2))*Category,
                data = df)
fit.R.all = brm(log2(OEV_biovolume_rotifers) ~ (TC_at_pulse+I(TC_at_pulse^2)),
                data = df)

pred.R.sep = conditional_effects(fit.R.sep,effects = "TC_at_pulse:Category",prob = 0.95)
pred.R.all = conditional_effects(fit.R.all,effects = "TC_at_pulse",prob = 0.95)

df_pred.R.sep = data.frame(cbind(pred.R.sep$`TC_at_pulse:Category`$effect2__,
                                 pred.R.sep$`TC_at_pulse:Category`$effect1__,
                                 pred.R.sep$`TC_at_pulse:Category`$estimate__,
                                 pred.R.sep$`TC_at_pulse:Category`$lower__,
                                 pred.R.sep$`TC_at_pulse:Category`$upper__))
names(df_pred.R.sep) <- c("Category","TC_at_pulse","Estimate","Lower","Upper")

df_pred.R.all = data.frame(cbind(pred.R.all$`TC_at_pulse`$effect1__,
                                 pred.R.all$`TC_at_pulse`$estimate__,
                                 pred.R.all$`TC_at_pulse`$lower__,
                                 pred.R.all$`TC_at_pulse`$upper__))
names(df_pred.R.all) <- c("TC_at_pulse","Estimate","Lower","Upper")

## Quadratic effects
# monocultures
hypothesis(fit.R.sep, "ITC_at_pulseE2<0") 
# polycultures
hypothesis(fit.R.sep, "ITC_at_pulseE2+(ITC_at_pulseE2:CategoryPolycultures)<0") 
# all
hypothesis(fit.R.all, "ITC_at_pulseE2<0")

### PLOTTING ###################################################################
figure2a <-  ggplot()+
  geom_ribbon(data=df_pred.A.all,
              aes(x=TC_at_pulse,ymin=Lower,ymax=Upper),fill='#FFA500',alpha=.1)+
  geom_ribbon(data=df_pred.A.sep%>%filter(Category==1),
              aes(x=TC_at_pulse,ymin=Lower,ymax=Upper),fill='steelblue',alpha=.1)+
  geom_ribbon(data=df_pred.A.sep%>%filter(Category==2),
              aes(x=TC_at_pulse,ymin=Lower,ymax=Upper),fill='black',alpha=.1)+
  geom_line(data=df_pred.A.sep%>%filter(Category==1),
            aes(x=TC_at_pulse,y=Estimate),color='steelblue',lwd=1.5,lty='dotted')+
  geom_line(data=df_pred.A.sep%>%filter(Category==2),
            aes(x=TC_at_pulse,y=Estimate),color='black',lwd=1.5,lty='dashed')+
  geom_line(data=df_pred.A.all,
            aes(x=TC_at_pulse,y=Estimate),color='#FFA500',lwd=2.5)+
  geom_point(data=df,aes(x=TC_at_pulse,y=log2(OEV_biovolume_algae),
                         color=Treatment,shape=Treatment),size=4)+
  scale_color_manual("",values=c("Bc"='steelblue','Ce'='steelblue',"Le"="steelblue",
                                 "9d"="black","13d"="black"))+
  
  scale_shape_manual("",values=c("Bc"=21,'Ce'=22,"Le"=23,"9d"=25,"13d"=24))+
  xlab("TC")+
  ylab("log2 algal response")+ylim(-3,2.1)+ # 0.6
  theme(legend.position="none",text = element_text(size = 15))+
  geom_text(aes(x=0,y=1.9,label='a)'),size=5)

figure2b <-  ggplot()+
  geom_ribbon(data=df_pred.R.all,
              aes(x=TC_at_pulse,ymin=Lower,ymax=Upper),fill='#FFA500',alpha=.1)+
  geom_ribbon(data=df_pred.R.sep%>%filter(Category==1),
              aes(x=TC_at_pulse,ymin=Lower,ymax=Upper),fill='steelblue',alpha=.1)+
  geom_ribbon(data=df_pred.R.sep%>%filter(Category==2),
              aes(x=TC_at_pulse,ymin=Lower,ymax=Upper),fill='black',alpha=.1)+
  geom_line(data=df_pred.R.sep%>%filter(Category==1),
            aes(x=TC_at_pulse,y=Estimate),color='steelblue',lwd=1.5,lty='dotted')+
  geom_line(data=df_pred.R.sep%>%filter(Category==2),
            aes(x=TC_at_pulse,y=Estimate),color='black',lwd=1.5,lty='dashed')+
  geom_line(data=df_pred.R.all,
            aes(x=TC_at_pulse,y=Estimate),color='#FFA500',lwd=2.5)+
  geom_point(data=df,aes(x=TC_at_pulse,y=log2(OEV_biovolume_rotifers),
                         color=Treatment,shape=Treatment),size=4)+
  scale_color_manual("",values=c("Bc"='steelblue','Ce'='steelblue',"Le"="steelblue",
                                 "9d"="black","13d"="black"))+
  
  scale_shape_manual("",values=c("Bc"=21,'Ce'=22,"Le"=23,"9d"=25,"13d"=24))+
  xlab("TC")+
  ylab("log2 rotifer response")+ ylim(-3,2.1)+ # 0.6
  theme(legend.position="none",text = element_text(size = 15))+
  geom_text(aes(x=0,y=1.9,label='b)'),size=5)

df_legend <- data.frame(Treatment=c("Bc","Ce","Le","9d","13d"),
                        relatBiovolume=c(.08,.08,.08,.08,.08),
                        Stability=c(0.74, 0.68, 0.62, 0.37, 0.31))
df_legend2 <- data.frame(Category = c("Fit Mono","Fit Mono",
                                      "Fit Poly","Fit Poly",
                                      "Fit All","Fit All"),
                         relatBiovolume=rep(c(.03,.15),3),
                         Stability=rep(c(.56,.25,.9),each=2) )
size_tlegend <- 5
legend <- ggplot()+
  geom_point(data=df_legend,
             aes(x=relatBiovolume,y=Stability,color=Treatment,shape=Treatment),
             size=4,alpha=.8)+
  geom_text(data=df_legend,
            aes(x=0.1+relatBiovolume,y=Stability,label=Treatment),
            size=size_tlegend)+
  
  geom_line(data=df_legend2,aes(x=relatBiovolume,y=Stability,color=Category,
                                linetype=Category,linewidth=Category))+
  geom_text(data=df_legend2%>%filter(relatBiovolume==0.15),
            aes(x=0.05+relatBiovolume,y=Stability,label=Category),
            size=size_tlegend,hjust=0)+
  geom_text(aes(x=0.2,y=0.8,label="Monocultures"),size=size_tlegend)+
  geom_text(aes(x=0.2,y=0.43,label="Polycultures"),size=size_tlegend)+
  scale_color_manual("",values=c("Bc"='steelblue','Ce'='steelblue',"Le"="steelblue",
                                 "9d"="black","13d"="black",
                                 "Fit Mono"='steelblue',"Fit Poly"="black",
                                 "Fit All"='#FFA500'))+
  scale_shape_manual("",values=c("Bc"=21,'Ce'=22,"Le"=23,"9d"=25,"13d"=24))+
  scale_linetype_manual("",values=c("Fit Mono"='dotted',"Fit Poly"="dashed",
                                    "Fit All"="solid"))+
  scale_linewidth_manual("",values=c("Fit Mono"=1.5,"Fit Poly"=1.5,"Fit All"=2.5))+
  xlab("")+ ylab("")+ xlim(0,1)+ylim(0,1)+
  theme_void()+
  theme(legend.position="none")

ggsave("figure2.pdf",
       grid.arrange(grobs=list(figure2a,figure2b,legend),
                    nrow=1),path = "./figures", height = 4, width = 8, dpi = 300)

