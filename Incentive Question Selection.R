# Change working directory.
setwd("C:/<YOURFAVORITEFOLDER>")
# Windows-specific internet connection
setInternet2(use = TRUE)
# Download and read file.
download.file("http://datamart.scicast.org/question/?format=csv&api_key=<YOURKEYHERE>",destfile="question_report.csv")
download.file("http://datamart.scicast.org/trade_history/?format=csv&api_key=<YOURKEYHERE>",destfile="trade_history_report.csv")
download.file("http://datamart.scicast.org/person/?format=csv&api_key=<YOURKEYHERE>",destfile="person_report.csv")
 qn<-read.csv("question_report.csv")
 th<-read.csv("trade_history_report.csv")
 pr<-read.csv("person_report.csv")

##############
# Setup
##############
tstart <- as.POSIXct("2013-11-25 00:00:00 EST");  base <- tstart-28*24*60*60; tstop <- tstart+floor(Sys.time()-tstart)-1*60*60

qiq <- qn$question_id; caq <- as.POSIXct(qn$created_at); grq <- as.character(qn$groups); saq <- as.character(qn$resolution_at); raq <- as.character(qn$pending_until)
#qn$provisional_settled_at is start of comment period and qn$pending_until will be reused for event resolution (not question resolution/settlement)
saq[saq=="None"] <- as.character(Sys.time()+10*365*60*60*24); saq <- as.POSIXct(saq)
raq[raq=="None"] <- as.character(Sys.time()+10*365*60*60*24); raq <- as.POSIXct(raq)
ls <- qn$relationships_source_question_id; ld <- qn$relationships_destination_question_id
ql <- qn$is_locked; qv <- qn$is_visible; qps <- qn$provisional_settled_at; pq <- qn$type
tpq <- rep(0,length(qiq)); tpq[pq=="binary"] <- 2; tpq[pq=="multi"] <- 3
ct <- qn$categories; orq <- qn$is_ordered; orq <- as.double(orq); rvq <- qn$resolution_value_array
drq <- as.double(raq-caq)

# Creating a matrix of questions' groups
gpq <- array(rep("a",length(qiq)*200),c(length(qiq),200)); pblk <- rep(0,length(qiq))
for (q in 1:length(qiq)) {
 temp <- as.vector(strsplit(grq[4],",")[[1]]); llt <- length(temp)
 gpq[q,1:llt] <- temp
 if ("Public"%in%temp) {pblk[q] <- 1}
}

#
# Removing admin accounts and activity
pip <- pr$user_id; pus <- as.character(pr$username); cap <- as.POSIXct(pr$created_at); grps <- pr$groups; rip <-pr$referral_id

#adu <- c("amsiegel","BAE11","brnlsl","brobins","cedarskye","christinafreyman","ctwardy","daggre_admin","dquere","gbs_tester","Inkling","jessiejury","jlu_bae","kennyth0","klaskey","kmieke","manindune","Naveen Jay","pthomas524","Question_Admin","Question Mark","randazzese","RobinHanson","saqibtq","scicast_admin","slin8","ssmith","tlevitt","wsun")
#adi <- numeric()
#for (i in 1:length(adu)) {
# adi[i] <- pip[pus==adu[i]]
# cap[pip==adi[i]] <- NA
#}

grp <- array(rep("a",length(pip)*20),c(length(pip),20)); igrp <- rep(0,length(pip))
for (i in 1:length(pip)) {
 temp <- as.vector(strsplit(as.character(grps[i]),",")[[1]])
 grp[i,1:length(temp)] <- temp
}
adi <- numeric()
for (i in 1:length(pip)) {
 for (g in 1:20) {
  if (grp[i,g]=="Admin"|grp[i,g]=="SuperAdmin"|grp[i,g]=="UserAdmin"|grp[i,g]=="BadgesAdmin"|grp[i,g]=="RolesAdmin"|grp[i,g]=="QuestionAdmin") {
   cap[i] <- NA
   adi <- c(adi,pip[i])
  }
  if (grp[i,g]=="Internal") {										# Keeping but noting internal accounts!
   igrp[i] <- 1
  }
 }
}
adi <- unique(adi)

good <- complete.cases(cap)
sum(!good)     												# How many are not good?
cap<-cap[good]; pus<-pus[good]; pip<-pip[good]; grp<-grp[good,]; rip<-rip[good]

pit <- th$user_id; qit <- th$question_id; tat <- as.POSIXct(th$traded_at)

for (i in 1:length(adi)) {
 tat[pit==adi[i]] <- NA
}
good <- complete.cases(tat)
sum(!good)     												# How many are not good?
tat<-tat[good]; pit<-pit[good]; qit<-qit[good]

#
# Removing stuttered forecasts

ord <- order(qit,tat)
tat<-tat[ord]; pit<-pit[ord]; qit<-qit[ord]
for (t in 1:(length(tat)-1)) {
 if (pit[t]==pit[t+1]&qit[t]==qit[t+1]&((tat[t+1]-base)-(tat[t]-base))<=0.25) {
  tat[t] <- NA
 }
}
good <- complete.cases(tat)
sum(!good)
tat<-tat[good]; pit<-pit[good]; qit<-qit[good]

##############
# Selecting Study questions
##############

pisq <- qiq[pblk==1&ql=="False"&qv=="True"&saq==max(saq)&raq>as.POSIXct("2014-11-15 00:00:00 EST")&qps=="None"]

#sort by pending_until; take first 300
ll <- min(length(pisq),300)
isq <- pisq[order(raq[qiq%in%pisq])][1:ll]

# Balance questions.
ntq <- rep(0,length(qiq))
for (q in 1:length(qiq)) {
 drq[q] <- as.double((raq[q]-base)-(caq[q]-base))
 ntq[q] <- length(pit[qit==qiq[q]])/drq[q]	# Edits per question per time unit
}

cq <- rep(0,length(qiq))
cq[is.na(ld)==F] <- 1

tq <- tpq
for (q in 1:length(qiq)) {
 if (orq[q]==2& tpq[q]==2) { tq[q]<-1 }	# scaled, continuous questions
}

# Hierarchical sort on factors before splitting even and odd
or <- order(tq[qiq%in%isq],raq[qiq%in%isq],ntq[qiq%in%isq],cq[qiq%in%isq])
isq <- isq[or]
sq1 <- seq(1,ll,2); sq2 <- seq(2,ll,2)
isq1 <- isq[sq1]; isq2 <- isq[sq2]

# Check
mean(tq[qiq%in%isq1]); mean(tq[qiq%in%isq2])
mean(cq[qiq%in%isq1]); mean(cq[qiq%in%isq2])
median(drq[qiq%in%isq1]); median(drq[qiq%in%isq2]); median(as.double(raq[qiq%in%isq1]-base)); median(as.double(raq[qiq%in%isq2]-base))
median(ntq[qiq%in%isq1]); median(ntq[qiq%in%isq2])

# Check that categories are evenly used.
wt <- rep(0,length(qiq))
cg <- array(numeric(), c(length(qiq),17))
for (j in 1:length(qiq)) {
 if(ct[j]!="") {
  temp <- levels(factor(strsplit(as.character(ct[j]),",")[[1]]))
  wt[j]<-1/length(temp); cg[j,1:(length(temp))]<- temp
 }
}
# Only physics is off.
temp1 <- as.vector(cg[which(qiq%in%isq1),]); temp1 <- temp1[is.na(temp1)==F]
temp2 <- as.vector(cg[which(qiq%in%isq2),]); temp2 <- temp2[is.na(temp2)==F]
ctgry <- "Physics"
length(temp1[temp1==ctgry]); length(temp2[temp2==ctgry])

# Printing table
write.table(data.frame(isq1,isq2),file="2014-15_incentive_questions.csv",sep=",",append=F,col.names=c("group_1_questio_id","group_2_question_id"),row.names=F)