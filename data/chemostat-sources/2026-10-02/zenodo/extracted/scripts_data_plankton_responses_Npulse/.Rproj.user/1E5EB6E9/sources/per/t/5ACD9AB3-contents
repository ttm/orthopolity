# Open the project scripts_data_plankton_responses_Npulse
### LIBRARIES ##################################################################
library(tidyverse)
library(PKNCA)

### LOADING and PREPARING DATA #################################################
## Experimental data
data <- read_excel("data/Chemostat_experimental_timeseries.xlsx")
df <- data.frame(data)

# Relabelling correctly the chemostats and setting correct variable type
WRONG_CHEMOSTATS <- c('1','2','3','4','5','6','7','8','9','10','11','12')
CORRECT_CHEMOSTATS <- c('001','002','003','004','005','006','007','008',
                        '009','010','011','012')
for (cs in 1:length(WRONG_CHEMOSTATS)){
  df$Chemostat[df$Chemostat == WRONG_CHEMOSTATS[cs]] <- CORRECT_CHEMOSTATS[cs]
}

df$Category <- as.factor(df$Category)
df$Treatment <- as.factor(df$Treatment)
df$Chemostat <- as.factor(df$Chemostat)
df$Time.standardised.to.pulse <- as.numeric(df$Time.standardised.to.pulse)

### FUNCTIONS ##################################################################
## Aim: calculating the biovolume responses of algae and rotifers
## Parameters: 
  # df_chemostat: a dataframe containing the biovolume timeseries of algae
    # and rotifer for a chemostat experiment
  # var_interest: the string "Biovolume_total_algae.µm..mL" or 
    #"Biovolume_total_rotifers.µm..mL" to select the algal or rotifer biovolume 
    # values and obtain the corresponding response
  # TIME_WINDOW: a numeric value determining the last sampling day to calculate 
    # the response
## Output:
  # oev: a numerical value of the biovolume response

calculate_biovolume_oev <-function(df_chemostat,var_interest,TIME_WINDOW){
  print(var_interest)
  if( (all(is.na(df_chemostat[var_interest]))) | (colMeans(df_chemostat[var_interest],na.rm=TRUE)==0) ){
    return(rep(NA,7))
  }else{
    df_chemostat <- df_chemostat[!is.na(df_chemostat[var_interest]),]
    df_chemostat <- df_chemostat[df_chemostat[var_interest]!=0,]
    
    pulse <- subset(df_chemostat,Time.standardised.to.pulse==0)
    post <- subset(df_chemostat,(Time.standardised.to.pulse>0)&(Time.standardised.to.pulse<TIME_WINDOW+1))
    interval <- max(post$Time.standardised.to.pulse)-min(post$Time.standardised.to.pulse)
    control = as.numeric(colMeans(pulse[var_interest]))
    post$absLRR <- as.numeric(sapply(post[var_interest], function(x) abs(log(x/control))))
    
    # biomass overall ecological stability
    oev <- pk.calc.auc(post$absLRR,
                       post$Time.standardised.to.pulse,
                       interval = c(min(post$Time.standardised.to.pulse), Inf))/interval
    return(oev)
  }
}

## Aim: calculating the biovolume and compositional responses of algae and 
  # rotifers, the top-down control at the pulse, the relative biovolume (share)
  # of each species per trophic level at the pulse
## Parameters: 
  # response: the dataframe where the ouputs of all chemostats are saved
  # df_chemostat: a dataframe containing the biovolume timeseries of algae
    # and rotifer for a chemostat experiment
  # category: the string "Monocultures" or "Polycultures"
  # chemostat: the string of the experimental unit
  # TIME_WINDOW: a numeric value determining the last sampling day to calculate 
    # the response
## Output:
  # response: the updated dataframe where the ouputs of all chemostats are saved

calculate_response<- function(response,df_chemostat,category,chemostat,TIME_WINDOW){

  # selecting timeseries at the pulse and after the pulse
  pulse <- subset(df_chemostat,Time.standardised.to.pulse==0)
  post <- subset(df_chemostat,(Time.standardised.to.pulse>0)&(Time.standardised.to.pulse<TIME_WINDOW+1))
  interval <- max(post$Time.standardised.to.pulse)-min(post$Time.standardised.to.pulse)
  
  # biovolume responses
  oev_biovolume_algae <- calculate_biovolume_oev(df_chemostat,
                                                 "Biovolume_total_algae.µm..mL",
                                                 TIME_WINDOW)
  oev_biovolume_rotifers <- calculate_biovolume_oev(df_chemostat,
                                                    "Biovolume_total_rotifers.µm..mL",
                                                    TIME_WINDOW)
  
  # saving responses, top-down control at the pulse, share of species at the pulse
  # for one experiment unit (chemostat)
  response_CS <- data.frame("Category"=c(category),
                            "Treatment"=c(df_chemostat$Treatment[1]),
                            "Chemostat"=c(chemostat),
                            "OEV_biovolume_algae"=c(oev_biovolume_algae),
                            "OEV_biovolume_rotifers"=c(oev_biovolume_rotifers),
                            "TC_at_pulse" = c(-log2(pulse$Biovolume_total_algae.µm..mL/3.72e7)),
                            "Relative_Biovolume_Monoraphidium_Chlorella_at_pulse" = c(pulse$Biovolume_Monoraphidium_Chlorella.µm..mL/pulse$Biovolume_total_algae.µm..mL),
                            "Relative_Biovolume_Chlamydomonas_at_pulse" = c(pulse$Biovolume_Chlamydomonas.µm..mL/pulse$Biovolume_total_algae.µm..mL),
                            "Relative_Biovolume_Cryptomonas_at_pulse" = c(pulse$Biovolume_Cryptomonas.µm..mL/pulse$Biovolume_total_algae.µm..mL),
                            "Relative_Biovolume_Brachionus_at_pulse" = c(pulse$Biovolume_Brachionus.µm..mL/pulse$Biovolume_total_rotifers.µm..mL),
                            "Relative_Biovolume_Cephalodella_at_pulse" = c(pulse$Biovolume_Cephalodella.µm..mL/pulse$Biovolume_total_rotifers.µm..mL),
                            "Relative_Biovolume_Lecane_at_pulse" = c(pulse$Biovolume_Lecane.µm..mL/pulse$Biovolume_total_rotifers.µm..mL)                             
    )
  return(rbind(response,response_CS))
}

### CALCULATING responses, top-down control and share of species at pulse ######
response <- data.frame("Category"=c(),
                       "Treatment"=c(),
                       "Chemostat"=c(),
                       "OEV_biovolume_algae"=c(),
                       "OEV_biovolume_rotifers"=c(),
                       "TC_at_pulse" = c(),
                       "Relative_Biovolume_Monoraphidium_Chlorella_at_pulse" = c(),
                       "Relative_Biovolume_Chlamydomonas_at_pulse" = c(),
                       "Relative_Biovolume_Cryptomonas_at_pulse" = c(),
                       "Relative_Biovolume_Brachionus_at_pulse" = c(),
                       "Relative_Biovolume_Cephalodella_at_pulse" = c(),
                       "Relative_Biovolume_Lecane_at_pulse" = c()                             
)

TIME_WINDOW <- 12 # consider short-term responses until 12 days after pulse
for (category in unique(df$Category)){
  df_category <- subset(df,Category==category)
  for (chemostat in unique(df_category$Chemostat)){
    df_chemostat <- subset(df_category,Chemostat==chemostat)
    print(c(category,chemostat))
    response <- calculate_response(response,df_chemostat,category,
                                   chemostat,TIME_WINDOW)
  }
}
# save calculations in data folder
write.table(response, file = "data/plankton_response_avgOEV_TC_share.csv",
            sep = ",", row.names = F)
