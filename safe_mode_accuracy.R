#!/usr/bin/env Rscript

#
# Pull csv files from data mart.
# Read  files pulled from Data Mart.

setwd("Data/")						# Use your favorite directory.
options <- commandArgs(trailingOnly = TRUE)		
apikey = options[1]					# Read the API key from the command line: Rscript safe_mode_accuracy.R <API_key>
print(apikey)
    
# Fetch the data from datamart to CSV files
#setInternet2(use = TRUE)    				# This only works on Windows.
base = "http://datamart.scicast.org/"
tail = paste("?format=csv&api_key=",apikey,sep="")
names = list("trade_history", "question_history", "question", "comment", "person")
for (i in 1:length(names)) {
    url = paste(base, names[i], "/", tail, sep="")
    filename = paste(names[i], "_report.csv", sep="")
    download.file(url, destfile=filename)
}

 th<-read.csv("trade_history_report.csv")
 qh<-read.csv("question_history_report.csv")
 qn<-read.csv("question_report.csv")
 cm<-read.csv("comment_report.csv")
 pr<-read.csv("person_report.csv")

#
# Removing admin accounts and activity
pip <- pr$user_id; pus <- as.character(pr$username); cap <- as.POSIXct(pr$created_at); grps <- pr$groups; rip <-pr$referral_id
adu <- c("amsiegel","BAE11","brnlsl","brobins","cedarskye","christinafreyman","ctwardy","daggre_admin","dquere","gbs_tester","Inkling","jessiejury","jlu_bae","kennyth0","klaskey","kmieke","manindune","Naveen Jay","pthomas524","Question_Admin","Question Mark","randazzese","RobinHanson","saqibtq","scicast_admin","slin8","ssmith","tlevitt","wsun")
adi <- numeric()
for (i in 1:length(adu)) {
 adi[i] <- pip[pus==adu[i]]
 cap[pip==adi[i]] <- NA
}

grp <- array(rep("a",length(pip)*20),c(length(pip),20)); igrp <- rep(0,length(pip))
for (i in 1:length(pip)) {
 temp <- as.vector(strsplit(as.character(grps[i]),",")[[1]])
 grp[i,1:length(temp)] <- temp
}
adi <- numeric()
# I think this removes all users with group "*Admin"
# TODO: Can't we just match endswith "Admin" instead of enumerating?
for (i in 1:length(pip)) {
 for (g in 1:20) {
  if (grp[i,g]=="Admin"|grp[i,g]=="SuperAdmin"|grp[i,g]=="UserAdmin"|grp[i,g]=="BadgesAdmin"|grp[i,g]=="RolesAdmin"|grp[i,g]=="QuestionAdmin") {
   cap[i] <- NA
   adi <- c(adi,pip[i])
  }
  if (grp[i,g]=="Internal") {										# Keeping but noting internal accounts
   igrp[i] <- 1
  }
 }
}
adi <- unique(adi)

good <- complete.cases(cap)
sum(!good)     												# How many are not good?
cap<-cap[good]; pus<-pus[good]; pip<-pip[good]; grp<-grp[good,]; rip<-rip[good]

pit <- th$user_id; qit <- th$question_id; tat <- as.POSIXct(th$traded_at); nvt <- th$new_value_list; ovt <- th$old_value_list; as <- th$serialized_assumptions; apot <- th$assets_per_option; tit <- th$trade_id
cit <- th$choice_index; rust <- as.character(th$raw_user_selection)

rst <- mdt <- rep(0,length(rust))
#for (t in 1:39) {
for (t in 1:length(rust)) {
 m <- strsplit(rust[t],",")[[1]][1]
 if (m!="None") {
  mdt[t] = 1
  tmp1 <- as.double(strsplit(as.vector(ovt[t]),",")[[1]])						# A later selection on SciCast.org like "Higher" will assume the user wants the forecast halfway between the current market estimate and the top of the bin.
  tmp2 <- strsplit(strsplit(rust[t],',')[[1]][4],'"',fixed=T)[[1]][2]
  if (is.na(tmp2)==T) { rst[t] <- mean(as.double(c( strsplit(strsplit(rust[t],",")[[1]][2],"[",fixed=T)[[1]][2], strsplit(strsplit(rust[t],",")[[1]][3],"]",fixed=T)[[1]][1] ))) }
  if (is.na(tmp2)==F) { 
  if (tmp2=="Lower" ) { rst[t] <- tmp1[cit[t]+1] + (as.double(strsplit(strsplit(strsplit(rust[t],',')[[1]][2],',')[[1]][1],'[',fixed=T)[[1]][2]) -tmp1[cit[t]+1])/2 }
  if (tmp2=="Higher") { rst[t] <- tmp1[cit[t]+1] + (as.double(strsplit(strsplit(rust[t],',')[[1]][3],']',fixed=T)) -tmp1[cit[t]+1])/2 }
  if (tmp2=="What they are now") { rst[t] <- tmp1[cit[t]+1]}
  if (tmp2=="null") { rst[t] <- mean(as.double(c( strsplit(strsplit(rust[t],",")[[1]][2],"[",fixed=T)[[1]][2], strsplit(strsplit(rust[t],",")[[1]][3],"]",fixed=T)[[1]][1] ))) }
  }
 }
}

for (i in 1:length(adi)) {
 tat[pit==adi[i]] <- NA
}
good <- complete.cases(tat)
sum(!good)     												# How many are not good?
tat<-tat[good]; pit<-pit[good]; qit<-qit[good]; nvt<-nvt[good]; ovt<-ovt[good]; as<-as[good]; apot<-apot[good]; tit<-tit[good]
cit<-cit[good]; rst<-rst[good]; mdt<-mdt[good]

pic <- cm$user_id; cac <- as.POSIXct(cm$created_at); qic <- cm$question_id
for (i in 1:length(adi)) {
 cac[pic==adi[i]] <- NA
}
good <- complete.cases(cac)
sum(!good)     												# How many are not good?
cac<-cac[good]; pic<-pic[good]; qic<-qic[good]

##############
# Setup
##############
start <- as.POSIXct("2013-11-25 00:00:00 EST");  base <- start-28*24*60*60; stop <- start+floor(Sys.time()-start)-1*60*60
days <- seq(1,ceiling(as.double(stop - start)),1)

#
# Removing stuttered forecasts

ord <- order(qit,tat)
tat<-tat[ord]; pit<-pit[ord]; qit<-qit[ord]; nvt<-nvt[ord]; ovt<-ovt[ord]; as<-as[ord]; apot<-apot[ord]
cit<-cit[ord]; rst<-rst[ord]; mdt<-mdt[ord]
for (t in 1:(length(tat)-1)) {
 if (pit[t]==pit[t+1]&qit[t]==qit[t+1]&((tat[t+1]-base)-(tat[t]-base))<=0.25) {
  tat[t] <- NA
 }
}
good <- complete.cases(tat)
sum(!good)
tat<-tat[good]; pit<-pit[good]; qit<-qit[good]; nvt<-nvt[good]; ovt<-ovt[ord]; ovt<-ovt[good]; as<-as[good]; apot<-apot[good]
cit<-cit[good]; rst<-rst[good]; mdt<-mdt[good]

qiq <- qn$question_id; caq <- as.POSIXct(qn$created_at); grq <- as.character(qn$groups); raq <- as.character(qn$resolution_at) #(qn$provisional_settled_at)
raq[raq=="None"] <- as.character(Sys.time()+365*60*60*24); raq <- as.POSIXct(raq)
ls <- qn$relationships_source_question_id; ld <- qn$relationships_destination_question_id

#
# Market Accuracy (Updated on 2014-09-19)
# Binary and ordered means continuous; it makes no difference to BS, but it does make a difference on "poco" and "hit".

 nowish <- strsplit(as.character(stop), ' ')[[1]][1]
asq <- aso <- rep("a",length(tat))
for (t in 1:length(tat)) {
 asq[t] <- strsplit(as.character(as[t]),':')[[1]][1]
 aso[t] <- strsplit(as.character(as[t]),':')[[1]][2]
}
asqt <- as.double(asq); asot <- as.double(aso)
asqt[is.na(asqt)==T] <- -1; asot[is.na(asot)==T] <- -1

# Find resolved questions.
'%ni%' <- Negate('%in%')
gpq <- matrix(rep("a",length(qiq)*200),c(length(qiq),200)); vldq <- rep(0,length(qiq))
for (q in 1:length(qiq)) {
 tmp <- as.vector(strsplit(grq[q],',',fixed=T)[[1]]); lv <- length(tmp)
 if (lv>0) {  gpq[q,1:lv] <- tmp }
 if ("Invalid Questions"%ni%tmp) { vldq[q] <- 1 }
}

ctq <- qn$categories; orq <- qn$is_ordered; orq <- as.double(orq)
#rsq <- levels(factor(qiq[raq<=Sys.time()&caq>start]))
rsq <- levels(factor(qiq[raq<=Sys.time()&caq>start&ctq!="Study 2.1"&ctq!="Study 2.1,Study 2.1"&vldq==1]))
 frc <- numeric(); rqb <- length(rsq)
 for (q in 1:length(rsq)) {frc[q] <- length(tat[qit==rsq[q]&pit%in%pip[igrp==0]])}					# Removing questions that have almost no (non-internal) forecasts
 rsq <- rsq[frc>2]; rqa <- length(rsq)

rvq <- qn$resolution_value_array; svt <- rvqt <- rvqat<- array(rep(0,length(tat)*40),c(length(tat),40)); roqt <- roqat <-rep(-1,length(tat))
for (t in 1:length(tat)) {
 temp1 <- as.double(strsplit(strsplit(strsplit(as.character(rvq[qiq==qit[t]]),"[",fixed=T)[[1]][2],"]",fixed=T)[[1]],",")[[1]])
 if (is.na(temp1[1])==F) {
  rvqt[t,1:length(temp1)] <- temp1
  if (mdt[t]>0) {
   dflt <- (1-rst[t])/(length(temp1)-1); svt[t,1:length(temp1)] <- rep(dflt,length(temp1))
   svt[t,(cit[t]+1)] <- rst[t]
  }
  if (temp1[1]%%1==0) {													# Not mixture resolutions
   roqt[t] <- which(rvqt[t,]==1)-1
  }
 }
 if (asqt[t]%in%rsq) {
  temp2 <- as.double(strsplit(strsplit(strsplit(as.character(rvq[qiq==asqt[t]]),"[",fixed=T)[[1]][2],"]",fixed=T)[[1]],",")[[1]])
  if (is.na(temp2[1])==F) {
   rvqat[t,1:length(temp2)] <- temp2
   if (temp2[1]%%1==0) {
    roqat[t] <- which(rvqat[t,]==1)-1
   }
  }
 }
}

# Weight forecasts by how long they endure. Average over questions.
acqu <- acun <- acop <- nfqu <- rep(2,length(rsq)); pocos <- pocou <- pocoop <- hit <- hitop <- rep(0,length(rsq)); ra <- rep(start,length(rsq))
for (q in 1:length(rsq)) {
 ra[q] <- raq[qiq==rsq[q]]
 w <- which(tat%in%tat[qit==rsq[q]&asqt%in%c(-1,rsq)&asot==roqat&mdt==1])
 time <- c(tat[w],ra[q]); or <- order(time); time <- time[or]
 lt <- length(time); nfqu[q] <- lt-1; weight <- rep(1,lt-1)
  tmp1 <- as.double(strsplit(strsplit(strsplit(as.character(rvq[qiq==rsq[q]]),"[",fixed=T)[[1]][2],"]",fixed=T)[[1]],",")[[1]])
  acd <- actop <- rep(2,lt); pocotop <- hittop <- rep(0,lt)
# Assume the first trade lasted 24 hours because we don't have a record of how long the questions were paused after being published.
   acd[1] <- time[1]-base -(time[1]-24*60*60-base)
   pocotop[1] <- 1/length(tmp1)
   if (lt>1) {
    for (t in 1:(lt-1)) {
     acd[t+1] <- time[t+1]-base -(time[t]-base)
     b <- which(tmp1==max(tmp1))
    }
   }

  if (orq[qiq==rsq[q]]==2) {
   acttop <-rep(0,length(tmp1)-1)
   for (o in 1:(length(tmp1)-1)) {
    acttop[o] <- 2*(o/length(tmp1)-sum(tmp1[1:o]))^2
   }
   actop[1] <- sum(acttop)/(length(tmp1)-1)
   if (lt>1) {
   for (t in 1:(lt-1)) {
     tmp0 <- matrix(svt[w,],c(length(w),40))
      if (t<2) {
       tmp3 <- tmp0[or[t],1:length(tmp1)]
      }
      else {
       w2 <- which(pit[w]==pit[w][or[t]]); lw2 <- length(w2); if (lw2>1) {weight[w2] <- 0; weight[or[t]] <- 1}		# Removing older forecasts from the same user
       tmp3 <- colMeans(tmp0[or[1:t],1:length(tmp1)]*weight[or[1:t]]) # colMeans(tmp0[or[1:t],1:length(tmp1)])
      }						 					# ULinOP based on safe mode
    acttop <-rep(0,length(tmp1)-1)
    for (o in 1:(length(tmp1)-1)) {
     acttop[o]<-2*(sum(tmp3[1:o])-sum(tmp1[1:o]))^2
    }
    actop[t+1] <- sum(acttop)/(length(tmp1)-1)
    if (length(tmp1)>2) {
     pocotop[t+1] <- mean(tmp3[b])
     if (mean(which(tmp3==max(tmp3)))%in%b) {hittop[t+1] <- 1}
    }
    else {
     pocotop[t+1] <- NA
     hittop[t+1] <- NA
    }
   }
   }
  }
  if (orq[qiq==rsq[q]]==1) {
    actop[1] <- (length(tmp1)-1)*(1/length(tmp1))^2+(1-1/length(tmp1))^2
   if (lt>1) {
    for (t in 1:(lt-1)) {
     tmp0 <- matrix(svt[w,],c(length(w),40))
      if (t<2) {
       tmp3 <- tmp0[or[t],1:length(tmp1)]
      }
      else {
       w2 <- which(pit[w]==pit[w][or[t]]); lw2 <- length(w2); if (lw2>1) {weight[w2] <- 0; weight[or[t]] <- 1}		# Removing older forecasts from the same user
       tmp3 <- colMeans(tmp0[or[1:t],1:length(tmp1)]*weight[or[1:t]]) # colMeans(tmp0[or[1:t],1:length(tmp1)])
      }						 					# ULinOP based on safe mode

     actop[t+1]<-sum( (tmp3[1:length(tmp1)]-tmp1)^2 )
     pocotop[t+1] <- mean(tmp3[b])
     if (mean(which(tmp3==max(tmp3)))%in%b) {hittop[t+1] <- 1}
    }
   }
  }
  acop[q] <- sum(actop*acd)/sum(acd)
  pocoop[q] <-sum(pocotop*acd)/sum(acd)
  hitop[q] <- sum(hittop*acd)/sum(acd)
}

# acop is the Brier score on each question.  Running this file should put the means (over questions) of three forms of accuracy for safe-mode forecasts on the screen.
acopm <- mean(acop); print(acopm); print("Brier Score")
pocoopm<-mean(pocoop,na.rm=T); print(pocoopm); print("Percentage on correct option")
hitopm <- mean(hitop,na.rm=T); print(hitopm); print("Hit rate")
