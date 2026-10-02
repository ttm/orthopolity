# Open the project scripts_data_plankton_responses_Npulse
### LIBRARIES ##################################################################
rm(list=ls())

library("readxl")
library("stringr")
library("cmdstanr")      
library("deSolve")      
library("RColorBrewer")

### FUNCTION ###################################################################
# Aim: Equation-based model for the dynamics of nitrogen concentration N, algal
  # biomass A and rotifer biomass R
# Parameters:
  # t: vector with time values
  # N: vector with the values of nitrogen concentration, algal biomass and 
    # rotife biomass
  # parms: list with the parameter values
# Output:
  # dN: a list with the predicted values of nitrogen concentration, algal 
    # biomass and rotife biomass at time t

model_mono = function(t, N, parms){
  with(parms,{
    dN = rep(0,3)
    FRA = b*N[1]*N[2]/(K+N[1]) # nitrogen uptake by algae
    FRR = a*N[2]*N[3]/(1.0+a*h*N[2]) # rotifer feeding rate
    dN[1] = (80.0-N[1])*0.2 - FRA/eA # nitrogen concentration
    dN[2] = FRA - FRR - 0.2*N[2] # algal biomass  
    dN[3] = eR*FRR - m*N[3] - 0.2*N[3] # rotifer biomass
    return(list(dN))
  })
}

### DATA and COMPUTATIONS ######################################################

# read the a-priori distributions of the parameters
fit = readRDS(file = "data/fit_monocultures.rds")
plot.out = FALSE # make pdf output of plots ?
n.post = 1000 # number of posterior samples for plotting

post = fit$draws(format="matrix")
set.seed(100)
post = post[sample(1:nrow(post),n.post), ]

# plotting settings
col.alg = brewer.pal(4,"Dark2")
col.rot = brewer.pal(8,"Dark2")[c(6,7,8)]
plotsize = 6
while (!is.null(dev.list()))  dev.off()

# load the experimental timeseries
df = read_xlsx("data/Chemostat_experimental_timeseries.xlsx") |> as.data.frame()
df = df %>% filter(Category=="Monocultures")

df$Mixture = substring(df$Chemostat,1,2)
df$Replicate = substring(df$Chemostat,3,3)

mixtures = unique(df$Mixture)

time = df$`Time standardised to pulse`[1:20]

Bvol = array(NA,dim=c(3,4,2,20)) # 3 treats, 4 reps, 2 states (accumulated algae + 1 rotifer each), 20 times

for(i.mix in 1:3){
  df.sub = subset(df, Mixture==mixtures[i.mix])
  for(i.rep in 1:4){
    df.sub.sub = subset(df.sub, Replicate==i.rep)
    # Algae: Cr+Ca+(Mo+Co)
    Bvol[i.mix,i.rep,1, ] = as.numeric(df.sub.sub[, 7])+as.numeric(df.sub.sub[, 8])+as.numeric(df.sub.sub[, 9]) 
    # Rotifer: Br/Ce/Le
    Bvol[i.mix,i.rep,2, ] = as.numeric(df.sub.sub[, 10]) 
  }
}
str(Bvol)

for(i in 1:3){ # treats
  for(j in 1:2){ # reps
    for(k in 1:2){ # states
      for(l in 1:20){ # times
        Bvol[i,j,k,l] = Bvol[i,j,k,l]  |> round()
      }
    }
  }
}

str(Bvol)

data.stan = list(n_reps = 4,
                 n_days = length(time),
                 Bvol = Bvol,
                 time = time)


### PLOTTING ###################################################################

ID.species = c("Bc","Ce","Le")

pred <- data.frame("Chemostat"=c(),"Time.standardised.to.pulse"=c(),
                   "N.Q1"=c(),"N.Q2"=c(),"N.Q3"=c(),
                   "Biovolume.Q1_A"=c(),"Biovolume.Q2_A"=c(),"Biovolume.Q3_A"=c(),
                   "Biovolume.Q1_R"=c(),"Biovolume.Q2_R"=c(),"Biovolume.Q3_R"=c())  

for(i.spec in 1:3){
  for(i.rep in 1:4){
    
    if(plot.out) pdf(paste0("figures/fit_monocultures_",ID.species[i.spec],i.rep,".pdf"), width=1.2*plotsize, height=plotsize)
    
    print(i.rep)
    
    par(mfrow=c(1,1), mar=c(0,0,0,0), oma=c(4,4,4,1), las=1)
    layout(matrix(c(1,2), 2, 1, byrow = TRUE),
           widths=c(1), heights=c(7,2))
    
    ## pre-pulse predictions
    
    time.pre = seq(from=-17, to=0, length.out=100)
    
    pred.N.pre = matrix(NA, n.post, 100)
    pred.A.pre = matrix(NA, n.post, 100)
    pred.R.pre = matrix(NA, n.post, 100)
    
    # loop over posterior samples
    for(k in 1:n.post){
      pars = post[k, ]
      parameters = list(b = pars[, "b"],
                        K = exp(pars[, "Klog"]),
                        eA = exp(pars[, "eAlog"]),
                        a = exp(pars[, paste0("alog[",i.spec,"]")]),
                        h = exp(pars[, paste0("hlog[",i.spec,"]")]),
                        m = pars[, paste0("m[",i.spec,"]")],
                        eR = pars[, paste0("eR[",i.spec,"]")]
      )
      # pre-pulse
      initvals = exp(c( pars[, paste0("B0Nlog[",i.spec,",",i.rep,"]")],
                        pars[, paste0("B0Alog[",i.spec,",",i.rep,"]")],
                        pars[, paste0("B0Rlog[",i.spec,",",i.rep,"]")]
      ))
      out1 = ode(y = initvals,
                 times = time.pre,
                 func = model_mono,
                 parms = parameters) |> as.data.frame()
      
      pred.N.pre[k, ] = out1[,2]
      pred.A.pre[k, ] = out1[,3]
      pred.R.pre[k, ] = out1[,4]
    }
    
    # quantiles
    pred.N.pre.qs = apply(pred.N.pre, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
    pred.A.pre.qs = apply(pred.A.pre, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
    pred.R.pre.qs = apply(pred.R.pre, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
    
    ## post-pulse predictions
    
    time.post = seq(from=0, to=19, length.out=100)
    
    pred.N.post = matrix(NA, n.post, 100)
    pred.A.post = matrix(NA, n.post, 100)
    pred.R.post = matrix(NA, n.post, 100)
    
    # loop over posterior samples
    for(k in 1:n.post){
      pars = post[k, ]
      parameters = list(b = pars[, "b"],
                        K = exp(pars[, "Klog"]),
                        eA = exp(pars[, "eAlog"]),
                        a = exp(pars[, paste0("alog[",i.spec,"]")]),
                        h = exp(pars[, paste0("hlog[",i.spec,"]")]),
                        m = pars[, paste0("m[",i.spec,"]")],
                        eR = pars[, paste0("eR[",i.spec,"]")]
      )
      # pre-pulse
      initvals = exp(c( pars[, paste0("BTNlog[",i.spec,",",i.rep,"]")],
                        pars[, paste0("BTAlog[",i.spec,",",i.rep,"]")],
                        pars[, paste0("BTRlog[",i.spec,",",i.rep,"]")]
      ))
      out1 = ode(y = initvals,
                 times = time.post,
                 func = model_mono,
                 parms = parameters) |> as.data.frame()
      
      pred.N.post[k, ] = out1[,2]
      pred.A.post[k, ] = out1[,3]
      pred.R.post[k, ] = out1[,4]
    }
    
    # quantiles
    pred.N.post.qs = apply(pred.N.post, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
    pred.A.post.qs = apply(pred.A.post, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
    pred.R.post.qs = apply(pred.R.post, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
    
    ## plot
    
    # plot algae & rotifer
    plot(time,Bvol[i.spec,1,1, ], log="y", type="n", xlab="Time", ylab="Biovolume", 
         ylim=c(1e5,1e8), xlim=c(-17,19), xaxt="n", yaxt="n")
    abline(v=0, col="lightgrey")
    axis(1, labels=NA)
    axis(2, at=c(1e4, 5e4, 1e5, 5e5, 1e6, 5e6, 1e7, 5e7, 1e8),
     labels=c("1e+04","","1e+05","","1e+06","","1e+07","","1e+08"))
    
    polygon( c(time.pre, rev(time.pre)),
             c(pred.A.pre.qs[1, ], rev(pred.A.pre.qs[3, ])),
             border=NA,
             col=adjustcolor(col.alg[1], alpha.f=0.2)
    )
    polygon( c(time.pre, rev(time.pre)),
             c(pred.R.pre.qs[1, ], rev(pred.R.pre.qs[3, ])),
             border=NA,
             col=adjustcolor(col.rot[i.spec], alpha.f=0.2)
    )
    polygon( c(time.post, rev(time.post)),
             c(pred.A.post.qs[1, ], rev(pred.A.post.qs[3, ])),
             border=NA,
             col=adjustcolor(col.alg[1], alpha.f=0.2)
    )
    polygon( c(time.post, rev(time.post)),
             c(pred.R.post.qs[1, ], rev(pred.R.post.qs[3, ])),
             border=NA,
             col=adjustcolor(col.rot[i.spec], alpha.f=0.2)
    )
    
    lines(time.pre, pred.A.pre.qs[2, ], col=col.alg[1], lwd=2)
    lines(time.pre, pred.R.pre.qs[2, ], col=col.rot[i.spec], lwd=2)
    
    lines(time.post, pred.A.post.qs[2, ], col=col.alg[1], lwd=2)
    lines(time.post, pred.R.post.qs[2, ], col=col.rot[i.spec], lwd=2)
    
    lines(time[Bvol[i.spec,i.rep,1, ]>0], Bvol[i.spec,i.rep,1, Bvol[i.spec,i.rep,1, ]>0], lty=3, col=col.alg[1])
    points(time, Bvol[i.spec,i.rep,1, ], pch=16, col=col.alg[1])
    lines(time[Bvol[i.spec,i.rep,2, ]>0], Bvol[i.spec,i.rep,2, Bvol[i.spec,i.rep,2, ]>0], lty=3, col=col.rot[i.spec])
    points(time, Bvol[i.spec,i.rep,2, ], pch=16, col=col.rot[i.spec])
    
    # plot nitrogen
    plot(time,Bvol[i.spec,1,1, ], log="y", type="n", xlab="Time", ylab="Biovolume", 
         ylim=c(0.1,500), 
         xlim=c(-17,19), yaxt="n")
    abline(v=0, col="lightgrey")
    axis(2, at=c(0.1, 1, 10, 100),
         labels=c("0.1","1","10","100"))
    abline(h=80, col=4, lty=2)
    
    polygon( c(time.pre, rev(time.pre)),
             c(pred.N.pre.qs[1, ], rev(pred.N.pre.qs[3, ])),
             border=NA,
             col=adjustcolor(4, alpha.f=0.2)
    )
    polygon( c(time.post, rev(time.post)),
             c(pred.N.post.qs[1, ], rev(pred.N.post.qs[3, ])),
             border=NA,
             col=adjustcolor(4, alpha.f=0.2)
    )
    
    lines(time.pre, pred.N.pre.qs[2, ], col=4, lwd=2)
    lines(time.post, pred.N.post.qs[2, ], col=4, lwd=2)
    
    title(paste0(ID.species[i.spec],i.rep), outer=TRUE)
    
    if(plot.out) dev.off()
  
  # saving the predicted 1st, 2nd and 3rd quantiles of the nitrogen N, algal 
    # biovolume A, rotifer biovolume R per chemostat
  pred_reps <- data.frame("Chemostat"=c(rep(paste0(c("Bc","Ce","Le")[i.spec],i.rep),n.post)),
                          "Time.standardised.to.pulse"=c(time.pre,time.post),
                          "N.Q1"=c(pred.N.pre.qs[1, ],pred.N.post.qs[1, ]),
                          "N.Q2"=c(pred.N.pre.qs[2, ],pred.N.post.qs[2, ]),
                          "N.Q3"=c(pred.N.pre.qs[3, ],pred.N.post.qs[3, ]),
                          "Biovolume.Q1_A"=c(pred.A.pre.qs[1, ],pred.A.post.qs[1, ]),
                          "Biovolume.Q2_A"=c(pred.A.pre.qs[2, ],pred.A.post.qs[2, ]),
                          "Biovolume.Q3_A"=c(pred.A.pre.qs[3, ],pred.A.post.qs[3, ]),
                          "Biovolume.Q1_R"=c(pred.R.pre.qs[1, ],pred.R.post.qs[1, ]),
                          "Biovolume.Q2_R"=c(pred.R.pre.qs[2, ],pred.R.post.qs[2, ]),
                          "Biovolume.Q3_R"=c(pred.R.pre.qs[3, ],pred.R.post.qs[3, ]))
  pred <- rbind(pred,pred_reps)
  }
}

write.table(pred, file = "data/bayesian_predictions_monocultures.csv", sep = ",", row.names = F)
