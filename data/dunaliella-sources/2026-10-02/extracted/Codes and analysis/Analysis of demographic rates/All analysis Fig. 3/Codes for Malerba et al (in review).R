rm(list = ls(all = TRUE))

# Load required packages. Otherwise install with "install.packages()" function
library(car); library(plyr); library(ggplot2); library(reshape2);library(splitstackshape); library(cowplot); library(effects);library(nlme); library(effects); library(emmeans);library(visreg)


##############
# Set the location of the folder with all the date
dir.day = ""	# CHANGE THE DIRECTORY HERE
##############

setwd(dir.day)

# Load raw data
load("All raw data.RData")
load("SummaryData.RData")


# ==================================================
# Part 1. Non-linear modeling to calculate r and K

# if FIT = T, it will fit all curves (takes a few minutes)
# if FIT = F, it will load the data already saved
FIT = T



# Here we fit a curve for each well
ODrawF2 = function(x){
	
	# x = subset(AllData, Sample == "S.2" & Media == "N-Deplete")
	print(data.frame("Treat" = unique(x$Treat), "Sample" = unique(x$Sample), "Media" = unique(x$Media)))	
	
	Predict = c()
	AIC = c()
	listModels = list()

	Analysis.modI = 
	try(nls(log(BiovolUL) ~ ymax * exp(umin*(Day-tmax) - (umin/k)*(1-exp(-k*(Day - tmax)))),
		data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
		start = c("umin" = -0.1, "tmax" = 4, "ymax" = max(log(x$BiovolUL)) , "k" = 1)
			))

	if(class(Analysis.modI) == "try-error") {
        	NULL
    } else {
		AIC = rbind(AIC, data.frame("Mod" = "modI", "AIC" = AIC(Analysis.modI), "isConv" = Analysis.modI$convInfo$isConv))
		listModels$modI = (Analysis.modI)
	}


	Analysis.MM = 
	try(nls(log(BiovolUL) ~ SSmicmen(Day, Vm, K), 
		data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
		start = c("Vm" = max(log(x$BiovolUL)), "K" = 1)))

	if(class(Analysis.MM) == "try-error") {
        	NULL
    } else {
		AIC = rbind(AIC, data.frame("Mod" = "MM", "AIC" = AIC(Analysis.MM), "isConv" = Analysis.MM$convInfo$isConv))
		listModels$MM = (Analysis.MM)
	}

	Analysis.logis = 
	try(nls(log(BiovolUL) ~ SSlogis(Day, Asym, xmid, scal), 
		data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
		start = c("Asym" = max(log(x$BiovolUL)), "xmid" = 1, scal = 1/1.5)))
	
	if(class(Analysis.logis) == "try-error") {
        	NULL
    } else {
		AIC = rbind(AIC, data.frame("Mod" = "logis", "AIC" = AIC(Analysis.logis), "isConv" = Analysis.logis$convInfo$isConv))
		listModels$logis = (Analysis.logis)
	}	

	Analysis.fpl = 
	try(nls(log(BiovolUL) ~ SSfpl(Day, A, B, xmid, scal), 
	 	data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
	 	start = c("A" = 0, "B" = max(log(x$BiovolUL)), xmid = 1, scal = 1/1.5)))

	 if(class(Analysis.fpl) == "try-error") {
         	NULL
     } else {
		AIC = rbind(AIC, data.frame("Mod" = "fpl", "AIC" = AIC(Analysis.fpl), "isConv" = Analysis.fpl$convInfo$isConv))
		listModels$fpl = (Analysis.fpl)
	}	

	Analysis.gomp = 
	try(nls(log(BiovolUL) ~ SSgompertz(Day, Asym, B2, B3), 
	 	data = x, algorithm = "port", control = nls.control(minFactor = 1/10000, maxiter = 2000, warnOnly = T),
	 	start = c("Asym" = max(log(x$BiovolUL)), "B2" = 1, "B3" = 0.5)))

	 if(class(Analysis.gomp) == "try-error") {
         	NULL
     } else {
 		AIC = rbind(AIC, data.frame("Mod" = "gomp", "AIC" = AIC(Analysis.gomp), "isConv" = Analysis.gomp$convInfo$isConv))
		listModels$gomp = (Analysis.gomp)
	}

	AIC.conv = subset(AIC, isConv == T)
	whichBest = AIC.conv[which.min(AIC.conv[,2]),1]
	isConv = AIC.conv[which.min(AIC.conv[,2]),3]

	# Isolate the best-fitting model
	bestModel = eval(parse(text = paste0("listModels$", whichBest)))

	# Calculate the derivative of the fitted model
	time.def = seq(0,max(x$Day), length.out = 500)
	pred.fit = predict(bestModel, newdata = data.frame(Day = time.def))
	smooth = predict(smooth.spline(x = time.def, y = pred.fit), deriv = 0)
	deriv = predict(smooth.spline(x =  time.def, y = pred.fit), deriv = 1)
	deriv2 = predict(smooth.spline(x =  time.def, y = pred.fit), deriv = 2)

	# Get all data together
	Predict = data.frame("Day" = time.def, 
     				     "Pred"= pred.fit,
     				     "Mod" = whichBest,
     				     "Smooth" = smooth$y,
     				     "Deriv" = deriv$y,
     				     "Deriv2" = deriv2$y)

	# Save the parameters
	umax = max(Predict$Deriv)
	umin = min(Predict$Deriv)
	K = max(Predict$Pred)
	tmax = time.def[which(Predict$Deriv == max(Predict$Deriv))]
	flex = time.def[min(which((Predict$Deriv2)<0))]
	Bio_init = exp(Predict$Pred[1])
	#udiff = umax - uinit
	tk = time.def[which(Predict$Pred == K)]

	A = ggplot(data = x, aes(x = Day, y = log(BiovolUL))) +
	# ggplot(data = x, aes(x = Day, y = log(OD_BC_man))) +
	geom_point(aes(shape = Plate)) +
	geom_line(data = Predict, aes(y = Pred, x = Day), size = 0.5) +
	geom_line(data = Predict, aes(y = Smooth, x = Day), size = 1.5, linetype = "dashed") +
	ggtitle(whichBest) +
	guides(shape=FALSE)
	#geom_line(data = predGuestPars, aes(y = log(Pred), x = Day))
	
	B = ggplot(data = Predict, aes(x = Day, y = Deriv)) +
	geom_line() +
	ggtitle("First Derivative")

	C = ggplot(data = Predict, aes(x = Day, y = Deriv2)) +
	geom_line() +
	geom_vline(xintercept = flex, size = 0.3) +
	ggtitle("Second Derivative")

	Plots = plot_grid(A, B,C, labels = c("A", "B","C"), ncol = 3, align = "h")
	save_plot(paste0("nls.",unique(x$Sample),"_",unique(x$Media), ".pdf"), 
		Plots, ncol = 1, nrow = 1, base_height = 6, base_width = 8)

	data.frame("Treat" = unique(x$Treat), "Sample" = unique(x$Sample), "Media" = unique(x$Media), "WellRow" = unique(x$WellRow),
		"whichBest" = whichBest, "isConv" = isConv,
		umax, umin, K, tmax, tk, flex, Bio_init)
	
	}


if(FIT == T) {

	setwd(paste0(dir.day,"/Fits"))
	# Fit all curves
	DataSum_NoB = ddply(.data = AllData, .variables = c("Sample", "Media"), .fun = ODrawF2)
	
	# Add the size of each single replicate
	DataSum_NoB$Rep = as.numeric(substr(DataSum_NoB$Sample, 3,4))
	DataSum_NoB = merge(DataSum_NoB, SummaryData, by = c("Treat", "Rep", "Media"), all = T)

	# Now remove the trajectories that have not converged
	DataSum_conv = subset(DataSum_NoB, isConv == "TRUE")
	length(DataSum_conv[,1])
	length(DataSum_NoB[,1])

	# Remove outlier points with unreasonable UMAX
	DataSum_conv = subset(DataSum_conv, umax < 20)

	# Combine Treat and Media into single factor
	DataSum_conv$TreatMedia = interaction(DataSum_conv$Treat, DataSum_conv$Media)
	DataSum_conv$TreatMedia = factor(DataSum_conv$TreatMedia, levels = unique(DataSum_conv$TreatMedia))

	# Add size; volume fixed (manually)
	DataSum_conv_red = merge(DataSum_conv, SummaryData, by = c("Treat", "Rep", "Media"), all = T)

	save(DataSum_conv_red, file = "DataSum_conv_red.RData")
	setwd(dir.day)

} else {

	setwd(paste0(dir.day,"/Fits"))
	load(file = "DataSum_conv_red.RData")
	setwd(dir.day)

}

table(DataSum_conv_red[,c("Sample", "Media")])
table(DataSum_conv_red[c("whichBest","Media", "Treat")])

# Check that all treatments converged
DataSum_conv_red$Sample[DataSum_conv_red$isConv == F]

# Save the frequency table
table.whichBest = table(DataSum_conv_red$whichBest, DataSum_conv_red$Treat,DataSum_conv_red$Media)
write.csv(table.whichBest, file = "table.whichBest.csv")





# ==================================================
# Part 2. Linear mixed-models to evaluate the effects 
# of size-selection treatment (Treat) and type of nutrient limitation (Media)
# on max. growth rate (umax) and carrying capacity (K)



STATS = T

if(STATS == T){
# ----
# UMAX
# ----

umax.best = lme(log(umax) ~ -1+Treat:Media+ (Bio_init), random= ~1|Sample, data = DataSum_conv_red, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))

anova(umax.best)
plot(umax.best)


# Model validation
boxplot(residuals(umax.best, type = "pearson")~Media, data = DataSum_conv_red)
boxplot(residuals(umax.best, type = "pearson")~Treat, data = DataSum_conv_red)
scatterplot(residuals(umax.best, type = "pearson")~(Bio_init), data = DataSum_conv_red)




# ----
# K in tot biovol uL-1
# ----

# Check the importance of the fixed effects
k.best = lme(K ~ -1+Treat:Media + (Bio_init), random= ~1|Sample, data = DataSum_conv_red, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))


anova(k.best)
plot(k.best)


# Model validation
boxplot(residuals(k.best, type = "pearson")~Media, data = DataSum_conv_red)
boxplot(residuals(k.best, type = "pearson")~Treat, data = DataSum_conv_red)
scatterplot(residuals(k.best, type = "pearson")~(Bio_init), data = DataSum_conv_red)









# ----
# K in pop density uL-1
# ----


# Use calibration curves to convert K from biovolume into #cells
load("CalibrationCurve.biovolcount.sqrt.RData")
DataSum_conv_red$KCellsUL = predict(CalibrationCurve.biovolcount.sqrt, new = data.frame(
"TotBiovolume" = exp(DataSum_conv_red$K),
"Treat" = DataSum_conv_red$Treat))^2



# Check the importance of the fixed effects
KCellsUL.best = lme(log(KCellsUL) ~ -1+Treat:Media + (Bio_init), random= ~1|Sample, data = DataSum_conv_red, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))


anova(KCellsUL.best)
plot(KCellsUL.best)


# Model validation
boxplot(residuals(KCellsUL.best, type = "pearson")~Media, data = DataSum_conv_red)
boxplot(residuals(KCellsUL.best, type = "pearson")~Treat, data = DataSum_conv_red)
scatterplot(residuals(KCellsUL.best, type = "pearson")~(Bio_init), data = DataSum_conv_red)






# ------------------------------------------
# FINAL STATISTICS to report in Table 1:
umax.lme.Final = lme(log(umax) ~ -1+Treat*Media+ (Bio_init), random= ~1|Sample, data = DataSum_conv_red, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))
K.lme.Final = lme(K ~ -1+Treat*Media + (Bio_init), random= ~1|Sample, data = DataSum_conv_red, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))
KCellsUL.Final = lme(log(KCellsUL) ~ -1+Treat*Media + (Bio_init), random= ~1|Sample, data = DataSum_conv_red, method = "ML", 
  weights = varComb(varIdent(form = ~1|Treat), varIdent(form = ~1|Media)))

anova(umax.lme.Final)
anova(K.lme.Final)
anova(KCellsUL.Final)
# ------------------------------------------





# Calculate partial residuals
umax.best.visreg = visreg::visreg(umax.lme.Final, xvar = "Treat", by = "Media", plot = F)
k.best.visreg = visreg::visreg(K.lme.Final, xvar = "Treat", by = "Media", plot = F)
KCellsUL.best.visreg = visreg::visreg(KCellsUL.Final, xvar = "Treat", by = "Media", plot = F)


save(umax.best.visreg,umax.best,k.best.visreg,k.best,KCellsUL.best.visreg,KCellsUL.best,umax.lme.Final,K.lme.Final, file = "All stats.RData")

} else {

#load(file = "All stats.RData")
load(file = "All stats_FINAL.RData")

}





# Get partial residuals
umax.ParRes = umax.best.visreg$res
k.ParRes = k.best.visreg$res
KCellsUL.ParRes = KCellsUL.best.visreg$res

# Get estimated coefficients and confidence intervals
umax.Fit = umax.best.visreg$fit
umax.Fit$coefs = fixef(umax.best)[-1] + fixef(umax.best)[1]*umax.Fit$Bio_init
umax.Fit$LCI = intervals(umax.best)$fixed[-1,1]+ fixef(umax.best)[1]*umax.Fit$Bio_init
umax.Fit$UCI = intervals(umax.best)$fixed[-1,3]+ fixef(umax.best)[1]*umax.Fit$Bio_init

k.Fit = k.best.visreg$fit
k.Fit$coefs = fixef(k.best)[-1] + fixef(k.best)[1]*k.Fit$Bio_init
k.Fit$LCI = intervals(k.best)$fixed[-1,1]+ fixef(k.best)[1]*k.Fit$Bio_init
k.Fit$UCI = intervals(k.best)$fixed[-1,3]+ fixef(k.best)[1]*k.Fit$Bio_init

KCellsUL.Fit = KCellsUL.best.visreg$fit
KCellsUL.Fit$coefs = fixef(KCellsUL.best)[-1] + fixef(KCellsUL.best)[1]*KCellsUL.Fit$Bio_init
KCellsUL.Fit$LCI = intervals(KCellsUL.best)$fixed[-1,1]+ fixef(KCellsUL.best)[1]*KCellsUL.Fit$Bio_init
KCellsUL.Fit$UCI = intervals(KCellsUL.best)$fixed[-1,3]+ fixef(KCellsUL.best)[1]*KCellsUL.Fit$Bio_init

UMAX_final2 = ggplot() +
		geom_point(data = umax.ParRes, aes(x = Treat, y = exp(visregRes), col = Media), shape = 1, stroke = 0.8, alpha = 0.5, position = position_dodge(width=0.5)) +
		geom_pointrange(data = umax.Fit, aes(x = Treat, col = Media, fill = Media,y = exp(coefs), ymin = exp(LCI), ymax = exp(UCI)), position = position_dodge(width=0.5), size = 0.6, show.legend = F) +		
		#geom_boxplot(aes(x = Treat, y = visregRes, fill = Media), col = "black", width = 0.45, alpha = 0.3, position = position_dodge(width=0.5)) +
		#geom_point(aes(x = Treat, y = visregRes, col = Media),shape = 1, position = position_dodge(width=0.5), stroke = 0.8, show.legend = F) +
		#stat_summary(fun.data="mean_cl_boot", geom="errorbar", width=0.2,size = 1, position = position_dodge(width=0.5)) +
		#stat_summary(fun.y = "mean", size = 3, geom = "point", position = position_dodge(width=0.5)) +
		#geom_violin(data = DataSum_conv_red, aes(x = Treat, y = umax_ParRes, col = Media, fill = Media)) +
		#geom_pointrange(data = umax.effects,aes(ymin = exp(LCI), ymax = exp(UCI), y = exp(Mean)), position = position_dodge(width=0.5), size = 0.6) +
		#geom_line(aes(group=Media, col = Media), position = position_dodge(width=0.5), linetype = "dashed") +
		theme_bw(base_size = 12) +
		labs(x = "",
			 y = expression(paste("Max. population growth rate (", italic(r[max]), ")")),
			 col='Pre-trial nutrient history') +
		#scale_fill_manual(values= c("Grey", "White"), labels = light_labels) +
		theme(legend.direction = "horizontal",
			legend.justification = c(0.99, 0.99), 
			legend.position = c(1, 0.1), 
			legend.background = element_rect(size=NULL, linetype= NULL, colour = NULL,fill = NULL), 
			legend.title=element_text(size=8),
			legend.text=element_text(size=8),			
			# Remove grid lines
			panel.border = element_blank(),
			#panel.grid.major = element_blank(),
			#panel.grid.minor = element_blank(),
			axis.line = element_line(colour = "black"),
			axis.text.x=element_blank()) +
		guides(col = guide_legend(override.aes = list(shape = 19, alpha = 1)))



K_final2 = ggplot() +
		geom_point(data = k.ParRes, aes(x = Treat, y = exp(visregRes), col = Media), shape = 1, stroke = 0.8, alpha = 0.5, position = position_dodge(width=0.5), show.legend = F) +
		geom_pointrange(data = k.Fit, aes(x = Treat, col = Media, fill = Media,y = exp(coefs), ymin = exp(LCI), ymax = exp(UCI)), position = position_dodge(width=0.5), size = 0.6, show.legend = F) +		
		theme_bw(base_size = 12)+
		labs(x = "Size-selection treatment",
			 y = expression(paste("Max. Biovolume Reached (", italic(K),")")),
			 col='Pre-trial nutrient history:') +
		#scale_fill_manual(values= c("Grey", "White"), labels = light_labels) +
		theme(legend.justification = c(0.99, 0.99), 
			legend.position = c(0.35, 0.32), 
			legend.background = element_rect(size=NULL, linetype= NULL, colour = NULL,fill = NULL), 
			legend.title=element_text(size=10),
			legend.text=element_text(size=10),
			legend.key=element_blank(),
			# Remove grid lines
			panel.border = element_blank(),
			#panel.grid.major = element_blank(),
			#panel.grid.minor = element_blank(),
			axis.line = element_line(colour = "black")) +
		guides(col=F, fill = F)




Boxplot_final2 = cowplot::plot_grid(UMAX_final2,K_final2, labels = c("A","B"), ncol = 1, align = "v", hjust = 0, vjust = 1)
cowplot::save_plot("Fig3_UMAX and K_2.pdf", Boxplot_final2, ncol = 1, nrow = 1, base_height = 8, base_width = 6)



# K in pop density
KCellsUL_final = ggplot(data = DataSum_conv_red) +
		geom_point(data = KCellsUL.ParRes, aes(x = Treat, y = visregRes, col = Media), shape = 1, stroke = 0.8, alpha = 0.5, position = position_dodge(width=0.5)) +
		geom_pointrange(data = KCellsUL.Fit, aes(x = Treat, col = Media, fill = Media,y = coefs, ymin = LCI, ymax = UCI), position = position_dodge(width=0.5), size = 0.6, show.legend = F) +		
		theme_bw(base_size = 12) +
		labs(x = "Size-selection treatment",
			 y = expression(paste("Max. Biovolume Reached in cells ",mu,"L"^-1,"(log"[e]," ", italic(K),")")),
			 col='Pre-trial nutrient history:') +
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

ggsave("FigS4_KCELLSUL.pdf", KCellsUL_final, height = 6, width = 6, device = "pdf")









