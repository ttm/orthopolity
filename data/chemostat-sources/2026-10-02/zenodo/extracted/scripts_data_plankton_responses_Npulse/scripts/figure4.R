### LIBRARIES and THEME SETTINGS ##############################################
library(tidyverse)
library(gridExtra)
library(scales)
library(cmdstanr) 

theme_set(theme_bw())
theme_update(plot.title = element_text(hjust = 0.5))

### FUNCTIONS #################################################################

# Aim: get the 1st, 2nd and 3rd quantiles of the nitrogen uptake by algae FA 
# predicted via Bayesian modelling depending on the nitrogen values N and 
# the chemostat
# Parameters:
# post: a dataframe with the posterior-distributions generated via Bayesian 
# modelling of the parameters eAlog the logarithm of the conversion factor 
# between N and algal biomass A,  b the maximum growth rate and Klog the 
# logarithm of the half-saturation constant
# N: a vector with nitrogen values
# label: string with name of the chemostat ("Mono" for monocultures, "Bc" for
# monocultures of B. calyciflorus, "Ce" for monocultures of Cephalodella sp.,
# "Le" for monocultures of Lecane sp., "Poly" for polycultures)
# Output:
# df: a dataframe with the 1st, 2nd and 3rd quantiles of the nitrogen uptake 
# by algae FA predicted via Bayesian modelling per N value and chemostat

get_FA <- function(post,N,label){
  post <- as.data.frame(post)
  df <- data.frame("Chemostat"=c(),"N"=c(),"FA.Q1"=c(),"FA.Q2"=c(),"FA.Q3"=c())
  for(Ni in N){
    post <- post %>% mutate(FA = exp(eAlog)*b*Ni/(Ni+exp(Klog)))
    FA.qs <- quantile(post$FA, probs=c(0.05, 0.5, 0.95))
    df <- rbind(df, data.frame("Chemostat"=c(label),"N"=c(Ni),"FA.Q1"=c(FA.qs[1]),
                               "FA.Q2"=c(FA.qs[2]),"FA.Q3"=c(FA.qs[3])))
  }
  return(df)}

# Aim: get the 1st, 2nd and 3rd quantiles of the per-capita net growth rates of 
# rotifers NGR predicted via Bayesian modelling depending on the algal biomass
# A and the chemostat
# Parameters:
# post: a dataframe with the posterior-distributions generated via Bayesian 
# modelling of the parameters eR the conversion factor between algae and
# rotifers, alog the logarithm of the rotifer attack rate, hlog the
# logarithm of the handling time, m the rotifer natural mortality rate
# A: a vector with algal biomass values
# label: string with name of the chemostat ("Mono" for monocultures, "Bc" for
# monocultures of B. calyciflorus, "Ce" for monocultures of Cephalodella sp.,
# "Le" for monocultures of Lecane sp., "Poly" for polycultures)
# Output:
# df: a dataframe with the 1st, 2nd and 3rd quantiles of the per-capita net  
# growth rates of rotifers NGR predicted via Bayesian modelling per A value 
# and chemostat

get_NGR <- function(post,A,label){
  post <- as.data.frame(post)
  df <- data.frame("Chemostat"=c(),"A"=c(),"NGR.Q1"=c(),"NGR.Q2"=c(),"NGR.Q3"=c())
  for(Ai in A){
    post <- post %>% mutate(NGR = eR*exp(alog)*Ai/(1+exp(alog)*exp(hlog)*Ai)-(m+0.2))
    NGR.qs <- quantile(post$NGR, probs=c(0.05, 0.5, 0.95))
    df <- rbind(df, data.frame("Chemostat"=c(label),"A"=c(Ai),"NGR.Q1"=c(NGR.qs[1]),
                               "NGR.Q2"=c(NGR.qs[2]),"NGR.Q3"=c(NGR.qs[3])))
  }
  return(df)}

### DATA and COMPUTATIONS ######################################################
N <- seq(1,3.5e2,5) # vector with nitrogen values
A <- c(seq(1,9.99e3,10),seq(1e3,5e7,5e5)) # vector with algal biomass values

# Loading the data with the posterior-distributions of the parameters estimated
# for the polycultures
fit3H <- readRDS(file = "data/fit_polycultures.rds")
post3H <- as.data.frame(fit3H$draws(format="matrix"))

# Loading the data with the posterior-distributions of the parameters estimated
# for the monocultures
fit1H <- readRDS(file = "data/fit_monocultures.rds")
post1H <- as.data.frame(fit1H$draws(format="matrix"))
postBc <- post1H[,c("alog[1]","hlog[1]","eR[1]","m[1]")] %>% 
  `colnames<-`(c("alog","hlog","eR","m"))
postCe <- post1H[,c("alog[2]","hlog[2]","eR[2]","m[2]")] %>% 
  `colnames<-`(c("alog","hlog","eR","m"))
postLe <- post1H[,c("alog[3]","hlog[3]","eR[3]","m[3]")] %>% 
  `colnames<-`(c("alog","hlog","eR","m"))

dfFA <- rbind(get_FA(post1H,N,"Mono"),get_FA(post3H,N,"Poly"))
dfNGR <- rbind(get_NGR(postBc,A,"Bc"),get_NGR(postCe,A,"Ce"),
               get_NGR(postLe,A,"Le"),get_NGR(post3H,A,"Poly"))

### PLOTTING ###################################################################
df_points <- dfNGR %>% filter(A %in% c(11001000,41001000))

figure4a <- ggplot(data=dfNGR)+
  geom_ribbon(aes(x=A/1e7,ymin=NGR.Q1,ymax=NGR.Q3,fill=Chemostat),alpha=0.2)+
  geom_line(aes(x=A/1e7,y=NGR.Q2,color=Chemostat,linetype=Chemostat),
            lwd=1.2,alpha=0.9)+
  geom_point(data=df_points,aes(x=A/1e7,y=NGR.Q2,color=Chemostat,shape=Chemostat),
             size=5)+
  
  geom_hline(yintercept=0,color='grey60',linetype='dotted')+
  annotate("text",x=0.15,y=1.1,label="a)",size=5)+
  scale_color_manual("",values= c('Bc'='firebrick','Ce'='red','Le'='orange',
                                  'Poly'='black'))+
  scale_fill_manual("",values= c('Bc'='firebrick','Ce'='red','Le'='orange',
                                 'Poly'='black'))+  
  scale_linetype_manual("",values= c('Bc'='solid','Ce'='solid','Le'='solid',
                                     'Poly'='dashed'))+  
  scale_shape_manual("",values= c("Bc"=21,'Ce'=22,"Le"=23,"Poly"=NA))+    
  xlab(expression(paste('Algal biovolume (',10^7,µm^3,mL^-1,')',sep='')))+
  ylab(expression(paste('Per-capita net growth rates (',µm^3,mL^-1,d^-1,')',sep='')))+
  guides(colour = guide_legend(nrow = 2,title.position ='left'),
         fill = guide_legend(nrow = 2,title.position ='left'),
         linetype = guide_legend(nrow = 2,title.position ='left'),
         shape = guide_legend(nrow = 2,title.position ='left'))+
  theme(text = element_text(size = 12),
        legend.position=c(0.67,0.1),
        legend.margin=margin(c(0.2,0.2,0.2,0.2)),
        legend.key.size = unit(1.3,"line"))

figure4b <- ggplot(data=dfFA)+
  geom_vline(xintercept=80,color="grey50")+
  geom_vline(xintercept=320,color="grey50")+
  geom_ribbon(aes(x=N,ymin=FA.Q1/1e5,ymax=FA.Q3/1e5,
                  fill=Chemostat),alpha=0.2)+
  geom_line(aes(x=N,y=FA.Q2/1e5,color=Chemostat,linetype=Chemostat),
            lwd=1.2,alpha=0.9)+
  annotate("text",x=0,y=3.05,label="b)",hjust=-0.1,vjust=-1,size=5)+
  annotate("text",x=55,y=0,label="N0",size=5,color="grey50")+
  annotate("text",x=175,y=0,label="pulse",size=5,color="grey50")+
  scale_fill_manual("",values= c('Mono'='steelblue','Poly'='black'))+
  scale_color_manual("",values= c('Mono'='steelblue','Poly'='black'))+
  scale_linetype_manual("",values= c('Mono'='solid','Poly'='dashed'))+
  scale_x_continuous(trans='log10',
                     breaks = c(1,10,100,10**2.5),
                     labels = scales::trans_format("log10", scales::math_format(10^.x)))+
  xlab(expression(paste('N concentration (',µmol,' N.',L^-1,')',sep='')))+
  ylab(expression(paste('Nutrient uptake of algae (',10^5,µm^3,mL^-1,d^-1,')',sep='')))+
  guides(colour = guide_legend(nrow = 2,title.position ='left'),
         fill = guide_legend(nrow = 2,title.position ='left'),
         linetype = guide_legend(nrow = 2,title.position ='left'))+
  theme(text = element_text(size = 12),legend.position=c(0.25,0.9),
        legend.margin=margin(c(0.2,0.2,0.2,0.2)),
        legend.key.size = unit(1.3,"line"))

ggsave("figure4_new.pdf",
       grid.arrange(grobs=list(figure4a,figure4b),nrow=1),
       path = "./figures", height = 4, width = 6, dpi = 300)
