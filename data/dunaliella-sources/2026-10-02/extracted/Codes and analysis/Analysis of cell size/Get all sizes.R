library(stringr);library(gdata); library(plyr); library(effects); library(ggplot2)

rm(list = ls(all = TRUE))

# Set the location of the folder with all the date
dir.day = ""

setwd(dir.day)

# Load all raw meaasurements of each cell
load(file = "CombData.RData")


# Plot the distribution of sizes within individual lineages
ggplot(data = CombData, aes(y =log(Vol), x = Treat)) +
geom_boxplot(aes(col = as.factor(Rep))) +
facet_grid(.~Media)
ggsave("All Volumes.pdf", device = "pdf")


#######################################
# Calculate averages
#######################################


# Calculate the means for each lineage

SumFun = function(x) {
	
	Size = mean(x$Area)
	Vol = mean(x$Vol)
	Perim = mean(x$Perim.)
	Major = mean(x$Major)
	Minor = mean(x$Minor)
	Circ = mean(x$Circ.)

	SizeSE = sd(x$Area)/sqrt(length(x$Area))
	VolSE = sd(x$Vol)/sqrt(length(x$Vol))
	PerimSE = sd(x$Perim.)/sqrt(length(x$Perim.))
	MajorSE = sd(x$Major)/sqrt(length(x$Major))
	MinorSE = sd(x$Minor)/sqrt(length(x$Minor))
	CircSE = sd(x$Circ.)/sqrt(length(x$Circ.))

	results = data.frame(Size,Vol,Perim,Major,Minor,Circ,SizeSE, VolSE ,PerimSE,MajorSE,MinorSE,CircSE)

return(results)

}


SummaryData = ddply(CombData, c("Media", "Treat", "Rep"), SumFun)

save(SummaryData, file = "SummaryData.RData")
write.csv(SummaryData, file = "SummaryData.csv")






#################################
## Final plots for cell volume
#################################

library(ggplot2); library(cowplot)

ggplot(data = SummaryData, aes(y = Vol, x = Treat)) +
geom_boxplot(aes(fill = Media))
ggsave("Summary Volumes.pdf", device = "pdf")

ggplot(data = SummaryData, aes(y = Vol, x = Treat)) +
geom_boxplot() +
scale_y_log10(name = "", breaks = seq(1000, 16000, 2000)) +
facet_grid(.~Media)
ggsave("Summary Volumes (noLog).pdf", device = "pdf")

ggplot(data = SummaryData, aes(y = Circ, x = Treat)) +
geom_boxplot() +
facet_grid(.~Media)
ggsave("Summary Circularity.pdf", device = "pdf")




##############
# Circularity
##############

ggplot(data = SummaryData, aes(y = Circ, x = Treat, fill = Media)) +
	theme_bw(base_size = 12) +
	geom_boxplot() +
	labs(x = "Size-selection treatment",
	 	y = "Mean Cell Circularity",
	 	fill='Pre-trial nutrient status') +
	theme(legend.justification = c(0.99, 0.99), 
		legend.position = c(0.97, 0.2), 
		legend.background = element_rect(size=NULL, linetype= NULL, colour = NULL,fill = NULL), 
		legend.title=element_text(size=10),
		legend.text=element_text(size=10),
		legend.key=element_blank(),
		# Remove grid lines
		panel.border = element_blank(),
		panel.grid.major = element_blank(),
		panel.grid.minor = element_blank(),
		axis.line = element_line(colour = "black")) +
	#scale_fill_brewer(palette = "Greys") +
ggsave("Summary Circularity_red.pdf", device = "pdf", width = 5.6, height = 5.8)


















