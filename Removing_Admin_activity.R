# ___ means you must supply text to make the script run.
# Pull csv files from data mart.
# Read files pulled from Data Mart.

setwd("C:___")
download.file("http://datamart.scicast.org/trade_history/?format=csv&api_key=___",destfile="trade_history_report.csv")
 th<-read.csv("C:___trade_history_report.csv")
download.file("http://datamart.scicast.org/question_history/?format=csv&api_key=___",destfile="question_history_report.csv")
 qh<-read.csv("C:___question_history_report.csv")
download.file("http://datamart.scicast.org/question/?format=csv&api_key=___",destfile="question_report.csv")
 qn<-read.csv("C:___question_report.csv")
download.file("http://datamart.scicast.org/comment/?format=csv&api_key=___",destfile="comment_report.csv")
 cm<-read.csv("C:___comment_report.csv")
download.file("http://datamart.scicast.org/person/?format=csv&api_key=___",destfile="person_report.csv")
 pr<-read.csv("C:___person_report.csv")

# Removing admin accounts and activity
pip <- pr$user_id; pus <- as.character(pr$username); cap <- as.POSIXct(pr$created_at); grps <- pr$groups
adi <- numeric()
for (i in 1:length(adu)) {
 adi[i] <- pip[pus==adu[i]]
 cap[pip==adi[i]] <- NA
}

grp <- array(rep("a",length(pip)*20),c(length(pip),20))
for (i in 1:length(pip)) {
 temp <- as.vector(strsplit(as.character(grps[i]),",")[[1]])
 grp[i,1:length(temp)] <- temp
}
adi <- numeric()
for (i in 1:length(pip)) {
 for (g in 1:20) {
  if (grp[i,g]=="Internal"|grp[i,g]=="Admin"|grp[i,g]=="SuperAdmin"|grp[i,g]=="UserAdmin"|grp[i,g]=="BadgesAdmin"|grp[i,g]=="RolesAdmin"|grp[i,g]=="QuestionAdmin") {
   cap[i] <- NA
   adi <- c(adi,pip[i])
  }
 }
}
adi <- unique(adi)

good <- complete.cases(cap)
sum(!good) # How many are not good?
cap<-cap[good]; pus<-pus[good]; pip<-pip[good]; grps<-grps[good]

pit <- th$user_id; qit <- th$question_id; tat <- as.POSIXct(th$traded_at); nvt <- th$new_value_list; as <- th$serialized_assumptions
for (i in 1:length(adi)) {
 tat[pit==adi[i]] <- NA
}
good <- complete.cases(tat)
sum(!good) # How many are not good?
tat<-tat[good]; pit<-pit[good]; qit<-qit[good]; nvt<-nvt[good]; as<-as[good]

pic <- cm$user_id; cac <- as.POSIXct(cm$created_at); qic <- cm$question_id
for (i in 1:length(adi)) {
 cac[pic==adi[i]] <- NA
}
good <- complete.cases(cac)
sum(!good) # How many are not good?
cac<-cac[good]; pic<-pic[good]; qic<-qic[good]
