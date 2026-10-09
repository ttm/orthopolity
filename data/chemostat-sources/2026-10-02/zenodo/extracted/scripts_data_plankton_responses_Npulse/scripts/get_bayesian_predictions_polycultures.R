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

model_poly = function(t, N, parms){
  with(parms,{
    dN = rep(0,3)
    FRA = b*N[1]*N[2]/(K+N[1]) # nitrogen uptake by algae
    FRR = a*N[2]*N[3]/(1.0+a*h*N[2]) # rotifer feeding rate
    dN[1] = (80.0-N[1])*0.2 - FRA/eA # nitrogen concentration
    dN[2] = FRA - FRR - 0.2*N[2]  # algal biomass  
    dN[3] = eR*FRR - m*N[3] - 0.2*N[3] # rotifer biomass
    return(list(dN))
  })
}

### DATA and COMPUTATIONS ######################################################
# read the a-priori distributions of the parameters
fit = readRDS(file = "data/fit_polycultures.rds")
# make pdf output of plots ?
plot.out = FALSE
# number of posterior samples for plotting
n.post = 1000

post = fit$draws(format="matrix")
set.seed(100)
post = post[sample(1:nrow(post),n.post), ]

# plotting settings
plotsize = 6
cols = brewer.pal(4,"Dark2")
col.alg = brewer.pal(4,"Dark2")
col.rot =  brewer.pal(8,"Dark2")[c(6,7,8)]
while (!is.null(dev.list()))  dev.off()

# load the experimental timeseries
df = read_xlsx("data/Chemostat_experimental_timeseries.xlsx") |> as.data.frame()
df = df %>% filter(Category=="Polycultures")

time = df$`Time standardised to pulse`[1:18]

n.reps = 12

Bvol = array(NA,dim=c(n.reps,2,18)) # reps, 2 states, 18 times

for(i.rep in 1:n.reps){ # 1:12
  df.sub = subset(df, Chemostat==i.rep)
  Bvol[i.rep,1, ] = 
    as.numeric(df.sub[, 7]) + # Cr
    as.numeric(df.sub[, 8]) + # Ca
    as.numeric(df.sub[, 9]) # Mo+Co
  Bvol[i.rep,2, ] = 
    as.numeric(df.sub[, 11]) + # Br
    as.numeric(df.sub[, 12]) + # Ce
    as.numeric(df.sub[, 13]) # Le
}
str(Bvol)

# remove 1 datapoint:
Bvol[3,2,2]=0

# data is actually complete! ==> can drop if-statements in Stan code
# just some zeros for 4th and 6th state (Br,Le) --> only there if(...>0)
for(j in 1:n.reps){ # reps
  for(k in 1:2){ # states
    for(l in 1:18){ # times
      Bvol[j,k,l] = Bvol[j,k,l]  |> round()
    }
  }
}

str(Bvol)

data.stan = list(n_reps = n.reps,
                 n_days = length(time),
                 Bvol = Bvol[1:n.reps, , ],
                 time = time)

### PLOTTING ###################################################################
pred <- data.frame("Chemostat"=c(),"Time.standardised.to.pulse"=c(),
                   "N.Q1"=c(),"N.Q2"=c(),"N.Q3"=c(),
                   "Biovolume.Q1_A"=c(),"Biovolume.Q2_A"=c(),"Biovolume.Q3_A"=c(),
                   "Biovolume.Q1_R"=c(),"Biovolume.Q2_R"=c(),"Biovolume.Q3_R"=c())  

for(i.rep in 1:n.reps){

  if(plot.out) pdf(paste0("figures/fit_polycultures_",i.rep,".pdf"), width=1.2*plotsize, height=plotsize)
  
  print(i.rep)
  
  par(mfrow=c(1,1), mar=c(0,0,0,0), oma=c(4,4,4,1), las=1)
  layout(matrix(c(1,2), 2, 1, byrow = TRUE),
         widths=c(1), heights=c(7,2))
  
  ## pre-pulse predictions
  
  time.pre = seq(from=-13, to=0, length.out=100)
  
  pred.N.pre = matrix(NA, n.post, 100)
  pred.A.pre = matrix(NA, n.post, 100)
  pred.R.pre = matrix(NA, n.post, 100)

  # loop over posterior samples
  for(k in 1:n.post){
    pars = post[k, ]

    b = pars[, "b"]
    K = pars[, "Klog"] |> exp()
    eA = pars[, "eAlog"] |> exp()
    a = pars[, "alog"] |> exp() 
    h = pars[, "hlog"] |> exp() 
    eR = pars[, "eR"]
    m = pars[, "m"]
    
    parameters = list(b=b, K=K, eA=eA, a=a, h=h, eR=eR, m=m)
    
    # pre-pulse
    initvals = pars[, c(paste0("B0Nlog[",i.rep,"]"),
                        paste0("B0Alog[",i.rep,"]"),
                        paste0("B0Rlog[",i.rep,"]")
    )] |> exp()
      
    out1 = ode(y = initvals,
               times = time.pre,
               func = model_poly,
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
  
  time.post = seq(from=0, to=12, length.out=100)
  
  pred.N.post = matrix(NA, n.post, 100)
  pred.A.post = matrix(NA, n.post, 100)
  pred.R.post = matrix(NA, n.post, 100)
  
  # loop over posterior samples
  for(k in 1:n.post){
    pars = post[k, ]
    
    b = pars[, "b"]
    K = pars[, "Klog"] |> exp()
    eA = pars[, "eAlog"] |> exp()
    a = pars[, "alog"] |> exp() 
    h = pars[, "hlog"] |> exp() 
    eR = pars[, "eR"]
    m = pars[, "m"]
    
    parameters = list(b=b, K=K, eA=eA, a=a, h=h, eR=eR, m=m)
    
    # pre-pulse
    initvals = pars[, c(paste0("BTNlog[",i.rep,"]"),
                        paste0("BTAlog[",i.rep,"]"),
                        paste0("BTRlog[",i.rep,"]")
    )] |> exp()
    
    out1 = ode(y = initvals,
               times = time.post,
               func = model_poly,
               parms = parameters) |> as.data.frame()
    
    pred.N.post[k, ] = out1[,2]
    pred.A.post[k, ] = out1[,3]
    pred.R.post[k, ] = out1[,4]
  }
  
  # quantiles
  pred.N.post.qs = apply(pred.N.post, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
  pred.A.post.qs = apply(pred.A.post, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
  pred.R.post.qs = apply(pred.R.post, 2, function(x) quantile(x, probs=c(0.05, 0.5, 0.95)))
  
  # plot algae & rotifer
  plot(time,Bvol[i.rep,1, ], log="y", type="n", xlab="Time", ylab="Biovolume", 
       ylim=c(1e6,2e8), xlim=c(-13,12), xaxt="n", yaxt="n")
  abline(v=0, col="lightgrey")
  axis(1, labels=NA)
  axis(2, at=c(5e4, 1e5, 5e5, 1e6, 5e6, 1e7, 5e7, 1e8, 5e8, 1e9 ),
       labels=c("","1e+05","","1e+06","","1e+07","","1e+08","","1e+09"))
  
  polygon( c(time.pre, rev(time.pre)),
           c(pred.A.pre.qs[1, ], rev(pred.A.pre.qs[3, ])),
           border=NA,
           col=adjustcolor(col.alg[1], alpha.f=0.2)
  )
  polygon( c(time.pre, rev(time.pre)),
           c(pred.R.pre.qs[1, ], rev(pred.R.pre.qs[3, ])),
           border=NA,
           col=adjustcolor(col.rot[1], alpha.f=0.2)
  )
  polygon( c(time.post, rev(time.post)),
           c(pred.A.post.qs[1, ], rev(pred.A.post.qs[3, ])),
           border=NA,
           col=adjustcolor(col.alg[1], alpha.f=0.2)
  )
  polygon( c(time.post, rev(time.post)),
           c(pred.R.post.qs[1, ], rev(pred.R.post.qs[3, ])),
           border=NA,
           col=adjustcolor(col.rot[1], alpha.f=0.2)
  )

  lines(time.pre, pred.R.pre.qs[2, ], col=col.rot[1], lwd=2)
  lines(time.post, pred.R.post.qs[2, ], col=col.rot[1], lwd=2)
  lines( time[Bvol[i.rep,2, ]>0], Bvol[i.rep,2, Bvol[i.rep,2, ]>0], lty=3, col=col.rot[1])
  points(time[Bvol[i.rep,2, ]>0], Bvol[i.rep,2, Bvol[i.rep,2, ]>0], pch=16, col=col.rot[1])

  lines(time.pre, pred.A.pre.qs[2, ], col=col.alg[1], lwd=2)
  lines(time.post, pred.A.post.qs[2, ], col=col.alg[1], lwd=2)
  lines( time[Bvol[i.rep,1, ]>0], Bvol[i.rep,1, Bvol[i.rep,1, ]>0], lty=3, col=col.alg[1])
  points(time[Bvol[i.rep,1, ]>0], Bvol[i.rep,1, Bvol[i.rep,1, ]>0], pch=16, col=col.alg[1])

  # plot nitrogen
  plot(time,Bvol[i.rep,1, ], log="y", type="n", xlab="Time", ylab="Biovolume", 
       ylim=c(0.1,500), xlim=c(-13,12), yaxt="n")
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
  
  
  title(paste0(i.rep), outer=TRUE)
  
  if(plot.out){ dev.off() }
  
  # saving the predicted 1st, 2nd and 3rd quantiles of the nitrogen N, algal 
  # biovolume A, rotifer biovolume R per chemostat
  pred_reps <- data.frame("Chemostat"=rep(c("001","002","003","004","005","006",
                                            "007","008","009","010","011","012")[i.rep],n.post),
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

write.table(pred, file = "data/bayesian_predictions_polycultures.csv", sep = ",", row.names = F)
