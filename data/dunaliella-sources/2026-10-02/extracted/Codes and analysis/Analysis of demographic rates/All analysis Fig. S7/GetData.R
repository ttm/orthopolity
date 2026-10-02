rm(list = ls(all = TRUE))

# Load required packages. Otherwise install with "install.packages()" function
library(stringr);library(gdata); library(reshape2); library(effects);library(ggplot2); library(chron); library(plyr); library(nlme); library(cowplot); library(visreg)


##############
# Set the location of the folder with all the date
dir.day = ""	# CHANGE THE DIRECTORY HERE
##############

setwd(dir.day)


# Load the raw data
load(file = "AllData across shelves.RData")



# ==================================================
# Part 1. Non-linear modeling to calculate r and K

# if FIT = T, it will fit all curves (takes a few minutes)
# if FIT = F, it will load the data already saved
FIT = F


# Here we fit a curve for each well
ODrawF2 = function(x){
	
	# x = subset(AllData_NoB, Treat == "Small" & Rep == "2" & Media == "FSW")
	print(data.frame("Treat" = unique(x$Treat), "Rep" = unique(x$Rep), "Media" = unique(x$Media)))	
	
	Predict = c()
	AIC = c()
	listModels = list()


	Analysis.MM = 
	try(nls(log(BiovolUL) ~ SSmicmen(Hours, Vm, K), 
		data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
		start = c("Vm" = max(log(x$BiovolUL)), "K" = 20)), silent = T)

	if(class(Analysis.MM) == "try-error") {
        	NULL
    } else {
		AIC = rbind(AIC, data.frame("Mod" = "MM", "AIC" = AIC(Analysis.MM), "isConv" = Analysis.MM$convInfo$isConv))
		listModels$MM = (Analysis.MM)
	}

	Analysis.gomp = 
	try(nls(log(BiovolUL) ~ SSgompertz(Hours, Asym, B2, B3), 
	 	data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
	 	start = c("Asym" = max(log(x$BiovolUL)), "B2" = 10, "B3" = 0.5)), silent = T)

	 if(class(Analysis.gomp) == "try-error") {
         	NULL
     } else {
 		AIC = rbind(AIC, data.frame("Mod" = "gomp", "AIC" = AIC(Analysis.gomp), "isConv" = Analysis.gomp$convInfo$isConv))
		listModels$gomp = (Analysis.gomp)
	}

	Analysis.logis = 
	try(nls(log(BiovolUL) ~ SSlogis(Hours, Asym, xmid, scal), 
		data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
		start = c("Asym" = max(log(x$BiovolUL)), "xmid" = 10, scal = 1/1.5)), silent = T)
	
	if(class(Analysis.logis) == "try-error") {
        	NULL
    } else {
		AIC = rbind(AIC, data.frame("Mod" = "logis", "AIC" = AIC(Analysis.logis), "isConv" = Analysis.logis$convInfo$isConv))
		listModels$logis = (Analysis.logis)
	}


	Analysis.modI = 
	try(nls(log(BiovolUL) ~ ymax * exp(umin*(Hours-tmax) - (umin/k)*(1-exp(-k*(Hours - tmax)))),
		data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
		start = c("umin" = -0.1, "tmax" = 4, "ymax" = max(log(x$BiovolUL)) , "k" = 10)), silent = T)

	if(class(Analysis.modI) == "try-error") {
        	NULL
    } else {
		AIC = rbind(AIC, data.frame("Mod" = "modI", "AIC" = AIC(Analysis.modI), "isConv" = Analysis.modI$convInfo$isConv))
		listModels$modI = (Analysis.modI)
	}


	Analysis.fpl = 
	try(nls(log(BiovolUL) ~ SSfpl(Hours, A, B, xmid, scal), 
	 	data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
	 	start = c("A" = 0, "B" = max(log(x$BiovolUL)), xmid = 100, scal = 1/1.5)), silent = T)

	 if(class(Analysis.fpl) == "try-error") {
         	NULL
     } else {
		AIC = rbind(AIC, data.frame("Mod" = "fpl", "AIC" = AIC(Analysis.fpl), "isConv" = Analysis.fpl$convInfo$isConv))
		listModels$fpl = (Analysis.fpl)
	}	


	AIC.conv = subset(AIC, isConv == T)
	whichBest = AIC.conv[which.min(AIC.conv[,2]),1]
	isConv = AIC.conv[which.min(AIC.conv[,2]),3]

	# Isolate the best-fitting model
	bestModel = eval(parse(text = paste0("listModels$", whichBest)))

	# Calculate the derivative of the fitted model
	time.def = seq(min(x$Hours), max(x$Hours), length.out = 500)
	pred.fit = predict(bestModel, newdata = data.frame(Hours = time.def))
	smooth = predict(smooth.spline(x = time.def, y = pred.fit), deriv = 0)
	deriv = predict(smooth.spline(x =  time.def, y = pred.fit), deriv = 1)
	deriv2 = predict(smooth.spline(x =  time.def, y = pred.fit), deriv = 2)

	# Get all data together
	Predict = data.frame("Hours" = time.def, 
     				     "Pred"= pred.fit,
     				     "Mod" = whichBest,
     				     "Smooth" = smooth$y,
     				     "Deriv" = deriv$y,
     				     "Deriv2" = deriv2$y)

	# Save the parameters
	umax = max(Predict$Deriv)
	umin = min(Predict$Deriv)
	K = max(Predict$Pred)

	# tmax has changed... after how long did cells loose half their growth rate
	tmax10 = time.def[ which(abs(Predict$Deriv-(max(Predict$Deriv)/10)) == min(abs(Predict$Deriv-(max(Predict$Deriv)/10)))) ]
	tmax50 = time.def[ which(abs(Predict$Deriv-(max(Predict$Deriv)/5)) == min(abs(Predict$Deriv-(max(Predict$Deriv)/5)))) ]
	flex = time.def[min(which((Predict$Deriv2)<0))]
	Bio_init = exp(Predict$Pred[1])
	#udiff = umax - uinit
	tk = time.def[which(Predict$Pred == K)]

	A = ggplot(data = x, aes(x = Hours, y = log(BiovolUL))) +
	# ggplot(data = x, aes(x = Hours, y = log(OD_BC_man))) +
	geom_point(aes(shape = Plate)) +
	geom_line(data = Predict, aes(y = Pred, x = Hours), size = 0.5) +
	geom_line(data = Predict, aes(y = Smooth, x = Hours), size = 1.5, linetype = "dashed") +
	ggtitle(whichBest) +
	guides(shape=FALSE)
	#geom_line(data = predGuestPars, aes(y = log(Pred), x = Hours))
	
	B = ggplot(data = Predict, aes(x = Hours, y = Deriv)) +
	geom_line() +
	ggtitle("First Derivative")

	C = ggplot(data = Predict, aes(x = Hours, y = Deriv2)) +
	geom_line() +
	geom_vline(xintercept = flex, size = 0.3) +
	ggtitle("Second Derivative")

	Plots = plot_grid(A, B,C, labels = c("A", "B","C"), ncol = 3, align = "h")
	save_plot(paste0("nls.",unique(x$Treat),unique(x$Rep),"_",unique(x$Media), ".pdf"), 
		Plots, ncol = 1, nrow = 1, base_height = 6, base_width = 8)

	data.frame("Treat" = unique(x$Treat), "Treat" = unique(x$Treat), "Rep" = unique(x$Rep), "Media" = unique(x$Media), "WellRow" = unique(x$WellRow),
		"whichBest" = whichBest, "isConv" = isConv,
		umax, umin, K, tmax10,tmax50, tk, flex, Bio_init)
	#, umin,tmax,ymax,k,umax, "ResStdErr" = ResStdErr, "ResSSR" = ResSSR, "isConv" = convInfo
	#, "convInfo.MM" = convInfo.MM, "LOGvsMM" = LOGvsMM)
	
	}


if(FIT == T) {

	setwd(paste0(dir.day,"/Fits"))
	# Fit all curves
	DataSum_NoB = ddply(.data = AllData_NoB, .variables = c("Media", "Treat", "Rep"), .fun = ODrawF2)

	# Now remove the trajectories that have not converged
	DataSum_conv = subset(DataSum_NoB, isConv == "TRUE")
	length(DataSum_conv[,1])
	length(DataSum_NoB[,1])

	# Remove the points with unreasonable UMAX
	DataSum_conv = subset(DataSum_conv, umax < 60)

	# Adjust the factors
	DataSum_conv$Treat = factor(DataSum_conv$Treat, levels = c("Small", "Control", "Large"))
	DataSum_conv$Media = factor(DataSum_conv$Media, levels = c("FSW","Nfree","Pfree","NP"), labels = c("N and P free", "N-free", "P-free", "N and P full"))
	DataSum_conv$Sample = interaction(DataSum_conv$Treat, DataSum_conv$Rep)


	save(DataSum_conv, file = "DataSum_conv.RData")
	setwd(dir.day)

} else {

	setwd(paste0(dir.day,"/Fits"))
	load(file = "DataSum_conv.RData")
	setwd(dir.day)

}


# Outlier
DataSum_conv = subset(DataSum_conv, !(Media == "N and P full" & Treat == "Small" & Rep == 6))


# ==================================================
# Part 2. Linear mixed-models to evaluate the effects 
# of size-selection treatment (Treat) and type of nutrient limitation (Media)
# on carrying capacity (K)



K.lme0 = lme(K ~ -1+Treat:Media+ (Bio_init), random= ~1|Sample, data = DataSum_conv, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))
K.lme1 = lme(K ~ -1+Treat:Media+ (Bio_init), random= ~1|Sample, data = DataSum_conv, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))
K.lme2 = lme(K ~ -1+Treat:Media, random= ~1|Sample, data = DataSum_conv, method = "ML", 
  weights = varComb(varIdent(form = ~1|Media)))
K.lme3 = lme(K ~ -1+Treat:Media, random= ~1|Sample, data = DataSum_conv, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat)))
K.lme4 = lme(K ~ -1+Treat:Media, random= ~1|Sample, data = DataSum_conv, method = "ML")
K.lme5 = lme(K ~ -1+Treat:Media+ (Bio_init), random= ~1|Sample, data = DataSum_conv, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat)))
AIC(K.lme0,K.lme1,K.lme2,K.lme3,K.lme4,K.lme5)

# Best-fitting model
k.best = K.lme4
k.best2 = lme(K ~ Treat*Media, random= ~1|Sample, data = DataSum_conv, method = "ML")
# -----------------

anova(k.best2)

k.best.visreg = visreg::visreg(k.best2, xvar = "Treat", by = "Media", plot = F)


# Get partial residuals
k.ParRes = k.best.visreg$res

# Get estimated coefficients and confidence intervals
k.Fit = k.best.visreg$fit
k.Fit$coefs = fixef(k.best)
k.Fit$LCI = intervals(k.best)$fixed[,1]
k.Fit$UCI = intervals(k.best)$fixed[,3]


K_final = ggplot() +
		geom_point(data = k.ParRes, aes(x = Treat, col = Media, y = exp(visregRes)), shape = 1, stroke = 0.8, alpha = 0.5, position = position_dodge(width=0.5), show.legend = F) +
		geom_pointrange(data = k.Fit, aes(x = Treat, col = Media, fill = Media,y = exp(coefs), ymin = exp(LCI), ymax = exp(UCI)), position = position_dodge(width=0.5), size = 0.6, show.legend = F) +		
		theme_bw(base_size = 12) +
		labs(x = "",
			 y = expression(paste("Total Biovolume Reached (",mu,"m"^3," ", mu,"L"^-1,")")),
			 col='Growth conditions:') +
		#scale_fill_manual(values= c("Grey", "White"), labels = light_labels) +
		theme(legend.justification = c(0.99, 0.99), 
			legend.position = c(0.99, 0.99), 
			legend.background = element_rect(size=NULL, linetype= NULL, colour = NULL,fill = NULL), 
			legend.title=element_text(size=10),
			legend.text=element_text(size=10),
			legend.key=element_blank(),
			# Remove grid lines
			panel.border = element_blank(),
			#panel.grid.major = element_blank(),
			panel.grid.minor = element_blank(),
			axis.line = element_line(colour = "black")) +
		guides(col = guide_legend(override.aes = list(shape = 19, alpha = 1)))

ggsave("K_final.pdf", K_final, height = 4, width = 6, device = "pdf")
















