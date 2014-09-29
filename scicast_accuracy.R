#!/usr/bin/env Rscript

## scicast_accuracy.R
##
##  Copyright (c) 2014 Ken Olson and (c) George Mason University
##  This software was developed under U.S. Government contract number D11PC20062.
##  The U.S. Federal Government is granted unlimited rights as defined in FAR 52.227-14.
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
## 
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##
## PURPOSE
##   Fetch csv files from the SciCast Data Mart, clean the data (destutter,
##   drop Admin, flag Internal, select resolved Qs, remove lonely Qs,
##   weight forecasts by duration), calculate some summary statistics like
##   Brier, %age on correct option, and hit rate.
##   Creates matrices for further calculation and plotting, e.g.
##   for making Ken's calibration plots.
##
## USAGE
##   Rscript scicast_accuracy.R <API_key> [nofetch]
##     - <API_key> is your API key, e.g. 00ab0be13b8c38f5547a8231dd24247a
##     - nofetch tells it to use existing CSV files in Data/
##
## TODO:
##   Functions!  Modularity!
##
## 

strtail <- function(s,n=1) {
    if(n<0) 
        substring(s,1-n) 
    else 
        substring(s,nchar(s)-n+1)
}

purify_pr <- function(data) {
    ## Remove Admin accounts & activity from the person_report. Flag Internal users.
    ## Returns a bunch of tables
    ## 
    ## Admin accounts have group *Admin, eg: Admin, Super*, User*, Badges*, Roles*, Question*...
    ## Flag "Internal" users.
    ## 
    ## TODO: why is 'grp' etc. limited to 20?

    pip <- data$user_id
    pus <- as.character(data$username)
    cap <- as.POSIXct(data$created_at)
    grps <- data$groups
    rip <- data$referral_id
    grp <- array(rep("a",length(pip)*20),c(length(pip),20));
    igrp <- rep(0,length(pip))
    for (i in 1:length(pip)) {
        temp <- as.vector(strsplit(as.character(grps[i]),",")[[1]])
        grp[i,1:length(temp)] <- temp
    }
    adi <- numeric()
    ## Here is where we remove the *Admin users.  TODO: faster way?
    for (i in 1:length(pip)) {
        for (g in 1:20) {
            if (strtail(grp[i,g],5)=="Admin") {
                cap[i] <- NA
                adi <- c(adi,pip[i])
            }
            if (grp[i,g]=="Internal") {           # Keeping but noting internal accounts
                igrp[i] <- 1
            }
        }
    }
    adi <- unique(adi)
    list(pip=pip,pus=pus,cap=cap,rip=rip,grp=grp,igrp=igrp,adi=adi)
}

get_safemode <- function(data) {
    ## Parse out the safe-mode edits from the trade_data table.
    ##   data -- the trade history table, eg th
    ##
    ## Returns rst, mdt
    ## 
    ## Safe-mode asks for a bin.
    ## If that is not the current bin, we assume their estimate is the midpoint of the bin.
    ## Otherwise we ask "Higher", "Lower", or "What it is now"
    ##   * Higher -> halfway between current estimate and upper bin boundary
    ##   * Lower -> halfway between current estimate and lower bin boundary
    ##   * ..now -> the current estimate (has no trade effect, but records estimate)
    ##
    rust <- as.character(th$raw_user_selection)
    ovt <- th$old_value_list
    cit <- th$choice_index
    rst <- mdt <- rep(0,length(rust))
    
    for (t in 1:length(rust)) {
        m <- strsplit(rust[t],",")[[1]][1]
        if (m=="None") next 
        
        mdt[t] = 1
        tmp1 <- as.double(strsplit(as.vector(ovt[t]),",")[[1]])
        tmp2 <- strsplit(strsplit(rust[t],',')[[1]][4],'"',fixed=T)[[1]][2]
        if (is.na(tmp2)==T) {
            rst[t] <- mean(as.double(c(strsplit(strsplit(rust[t],",")[[1]][2],"[",fixed=T)[[1]][2], strsplit(strsplit(rust[t],",")[[1]][3],"]",fixed=T)[[1]][1] )))
        } else {
            if (tmp2=="Lower" ) {
                rst[t] <- tmp1[cit[t]+1] + (as.double(strsplit(strsplit(strsplit(rust[t],',')[[1]][2],',')[[1]][1],'[',fixed=T)[[1]][2]) -tmp1[cit[t]+1])/2
            } else if (tmp2=="Higher") {
                rst[t] <- tmp1[cit[t]+1] + (as.double(strsplit(strsplit(rust[t],',')[[1]][3],']',fixed=T)) -tmp1[cit[t]+1])/2
            } else if (tmp2=="What they are now") {
                rst[t] <- tmp1[cit[t]+1]
            } else if (tmp2=="null") {
                rst[t] <- mean(as.double(c( strsplit(strsplit(rust[t],",")[[1]][2],"[",fixed=T)[[1]][2], strsplit(strsplit(rust[t],",")[[1]][3],"]",fixed=T)[[1]][1] )))
            }
        }
    }
    list(rst=rst, mdt=mdt)
}


################

## Read API key and set working directory
setwd("Data/")					# Use your favorite directory.
options <- commandArgs(trailingOnly = TRUE)		
print(options)
apikey = options[1]				# Read the API key

FETCH <- TRUE
for (opt in options[2:length(options)]) {
    if (is.na(opt)) next
    if (tolower(opt) == "nofetch") {
        FETCH <- FALSE
    }
}

    
## Fetch the data from datamart to CSV files
if (FETCH) {
    if (Sys.info()['sysname'] == 'Windows') {
        setInternet2(use = TRUE)    		# This only works on Windows.
    }
    base = "http://datamart.scicast.org/"
    tail = paste("?format=csv&api_key=",apikey,sep="")
    names = list("trade_history", "question_history", "question", "comment", "person")
    for (i in 1:length(names)) {
        url = paste(base, names[i], "/", tail, sep="")
        filename = paste(names[i], "_report.csv", sep="")
        download.file(url, destfile=filename)
    }
}

## 
## Read the CSV files into *core* variables
##
print("Reading data from CSV files....")
th<-read.csv("trade_history_report.csv")
qh<-read.csv("question_history_report.csv")
qn<-read.csv("question_report.csv")
cm<-read.csv("comment_report.csv")
pr<-read.csv("person_report.csv")

## Parse user info
print("Parsing user info....")
data <- purify_pr(pr)
summary(data)
igrp <- data$igrp;
adi <- data$adi
good <- complete.cases(data$cap)
sum(!good)                                        # How many are not good?
cap<-data$cap[good];
pus<-data$pus[good];
pip<-data$pip[good];
grp<-data$grp[good,];
rip<-data$rip[good]

## Select the valid edits
print("Selecting valid edits....")
tat <- as.POSIXct(th$traded_at)
pit <- th$user_id
for (i in 1:length(adi)) {
    tat[pit==adi[i]] <- NA
}
good <- complete.cases(tat)
sum(!good)     					  # How many are not good?
tat <- tat[good];
pit <- pit[good];
qit <- th$question_id[good];
nvt <- th$new_value_list[good];
ovt <- th$old_value_list[good];
sas <- th$serialized_assumptions[good];
apot<- th$assets_per_option[good];
tit <- th$trade_id[good]
cit <- th$choice_index[good];
## Parse out the Safe-Mode estimates
print("Parsing Safe-Mode estimates...")
data <- get_safemode(th)
rst <- data$rst[good];
mdt <- data$mdt[good]

## Parse the comments
print("Parsing the comments....")
pic <- cm$user_id;
cac <- as.POSIXct(cm$created_at);
qic <- cm$question_id
for (i in 1:length(adi)) {
    cac[pic==adi[i]] <- NA
}
good <- complete.cases(cac)
sum(!good)     				          # How many are not good?
cac<-cac[good];
pic<-pic[good];
qic<-qic[good]

############################
## Setup
############################
tstart <- as.POSIXct("2013-11-25 00:00:00 EST");
base <- tstart-28*24*60*60;
tstop <- tstart+floor(Sys.time()-tstart)-1*60*60
days <- seq(1,ceiling(as.double(tstop - tstart)),1)

## Remove stuttered forecasts
print("Destuttering.......(this takes a few minutes)......")
ord <- order(qit,tat)
tat<-tat[ord];
pit<-pit[ord];
qit<-qit[ord];
nvt<-nvt[ord];
ovt<-ovt[ord];
sas<-sas[ord];
apot<-apot[ord];
cit<-cit[ord];
rst<-rst[ord];
mdt<-mdt[ord];
for (t in 1:(length(tat)-1)) {
    if (pit[t]==pit[t+1]&qit[t]==qit[t+1]&((tat[t+1]-base)-(tat[t]-base))<=0.25) {
        tat[t] <- NA
    }
}
good <- complete.cases(tat)
sum(!good)
tat<-tat[good];
pit<-pit[good];
qit<-qit[good];
nvt<-nvt[good];
ovt<-ovt[good];
sas<-sas[good];
apot<-apot[good]
cit<-cit[good];
rst<-rst[good];
mdt<-mdt[good]

## Parse question info
print("Parsing questions....")
qiq <- qn$question_id;
caq <- as.POSIXct(qn$created_at);
grq <- as.character(qn$groups);
raq <- as.character(qn$resolution_at) ##(qn$provisional_settled_at)
raq[raq=="None"] <- as.character(Sys.time()+365*60*60*24);
raq <- as.POSIXct(raq)
ls <- qn$relationships_source_question_id;
ld <- qn$relationships_destination_question_id


##############################################
## Market Accuracy (Updated on 2014-09-19)
##############################################

## Note: Binary and ordered means continuous;
## It makes no difference to Brier, but it does make a difference on "poco" and "hit".
print("*** Beginning to calculate accuracy ***")
nowish <- strsplit(as.character(tstop), ' ')[[1]][1]
asq <- aso <- rep("a",length(tat))
for (t in 1:length(tat)) {
    asq[t] <- strsplit(as.character(sas[t]),':')[[1]][1]
    aso[t] <- strsplit(as.character(sas[t]),':')[[1]][2]
}
asqt <- as.double(asq);
asot <- as.double(aso)
asqt[is.na(asqt)==T] <- -1;
asot[is.na(asot)==T] <- -1

## Find resolved questions.
print("Finding resolved Qs...")
'%ni%' <- Negate('%in%')
gpq <- matrix(rep("a",length(qiq)*200),c(length(qiq),200));
vldq <- rep(0,length(qiq))
for (q in 1:length(qiq)) {
    tmp <- as.vector(strsplit(grq[q],',',fixed=T)[[1]]);
    lv <- length(tmp)
    if (lv>0) {  gpq[q,1:lv] <- tmp }
    if ("Invalid Questions"%ni%tmp) { vldq[q] <- 1 }
}

ctq <- qn$categories;
orq <- qn$is_ordered;
orq <- as.double(orq)
##rsq <- levels(factor(qiq[raq<=Sys.time()&caq>tstart]))
rsq <- levels(factor(qiq[raq<=Sys.time()&caq>tstart&ctq!="Study 2.1"&ctq!="Study 2.1,Study 2.1"&vldq==1]))
frc <- numeric();
rqb <- length(rsq)

## Remove questions that have almost no (non-internal) forecasts
print("Removing lonely Qs...")
for (q in 1:length(rsq)) {frc[q] <- length(tat[qit==rsq[q]&pit%in%pip[igrp==0]])}
rsq <- rsq[frc>2];
rqa <- length(rsq)

rvq <- qn$resolution_value_array;
svt <- rvqt <- rvqat <- array(rep(0,length(tat)*40),c(length(tat),40));
roqt <- roqat <-rep(-1,length(tat))
for (t in 1:length(tat)) {
    temp1 <- as.double(strsplit(strsplit(strsplit(as.character(rvq[qiq==qit[t]]),"[",fixed=T)[[1]][2],"]",fixed=T)[[1]],",")[[1]])
    if (is.na(temp1[1])==F) {
        rvqt[t,1:length(temp1)] <- temp1
        if (mdt[t]>0) {
            dflt <- (1-rst[t])/(length(temp1)-1);
            svt[t,1:length(temp1)] <- rep(dflt,length(temp1))
            svt[t,(cit[t]+1)] <- rst[t]
        }
        if (temp1[1]%%1==0) {                     # Not mixture resolutions
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

## Weight forecasts by how long they endure. Average over questions.
print("Weighting foreasts by duration....")
acqu <- acun <- acop <- nfqu <- rep(2,length(rsq));
pocos <- pocou <- pocoop <- hit <- hitop <- rep(0,length(rsq));
ra <- rep(tstart,length(rsq))
base <- tstart-28*24*60*60        # TODO: why defining again?
for (q in 1:length(rsq)) {
    ra[q] <- raq[qiq==rsq[q]]
    w <- which(tat%in%tat[qit==rsq[q]&asqt%in%c(-1,rsq)&asot==roqat])
    time <- c(tat[w],ra[q]); or <- order(time); time <- time[or]
    lt <- length(time); nfqu[q] <- lt-1
    tmp1 <- as.double(strsplit(strsplit(strsplit(as.character(rvq[qiq==rsq[q]]),"[",fixed=T)[[1]][2],"]",fixed=T)[[1]],",")[[1]])
    ac <- acd <- act <- rep(2,lt);
    pocot <- hitt <- rep(0,lt)
    ## Pretend the first trade lasted 24 hours because we don't have a record
    ## of how long the questions were paused after being published.
    acd[1] <- time[1]-base -(time[1]-24*60*60-base)
    pocot[1] <- pocou[q] <- 1/length(tmp1)
    if (lt>1) {
        for (t in 1:(lt-1)) {
            acd[t+1] <- time[t+1]-base -(time[t]-base)
            tmp2 <- as.double(strsplit(as.vector(nvt[w])[or[t]],",")[[1]])
            b <- which(tmp1==max(tmp1))
        }
    }
    
    if (orq[qiq==rsq[q]]==2) {
        actt <-rep(0,length(tmp1)-1)
        for (o in 1:(length(tmp1)-1)) {
            actt[o] <- 2*(o/length(tmp1)-sum(tmp1[1:o]))^2
        }
        act[1] <- acun[q] <- sum(actt)/(length(tmp1)-1)
        if (lt>1) {
            for (t in 1:(lt-1)) {
                tmp2 <- as.double(strsplit(as.vector(nvt[w])[or[t]],",")[[1]])
                actt <-rep(0,length(tmp1)-1)
                for (o in 1:(length(tmp1)-1)) {
                    actt[o] <- 2*(sum(tmp2[1:o])-sum(tmp1[1:o]))^2
                }
                act[t+1] <- sum(actt)/(length(tmp1)-1)
                if (length(tmp1)>2) {
                    pocot[t+1] <- mean(tmp2[b])
                    if (mean(which(tmp2==max(tmp2)))%in%b) {hitt[t+1] <- 1}
                }
                else {
                    pocot[t+1] <- NA
                    hitt[t+1] <- NA
                }
            }
        }
    }
    if (orq[qiq==rsq[q]]==1) {
        act[1] <- acun[q] <- (length(tmp1)-1)*(1/length(tmp1))^2+(1-1/length(tmp1))^2
        if (lt>1) {
            for (t in 1:(lt-1)) {
                tmp2 <- as.double(strsplit(as.vector(nvt[w])[or[t]],",")[[1]])
                act[t+1] <- sum( (tmp2-tmp1)^2 )
                pocot[t+1] <- mean(tmp2[b])
                if (mean(which(tmp2==max(tmp2)))%in%b) {hitt[t+1] <- 1}
            }
        }
    }
    acqu[q] <- sum(act*acd)/sum(acd)
    pocos[q] <-sum(pocot*acd)/sum(acd)
    hit[q] <- sum(hitt*acd)/sum(acd)
}

## acop is the Brier score on each question.
## Running this file should put the means (over questions) of three forms
## of accuracy for edits on the screen.
print("\\n::::::::::::::::")
print("Results Summary:")
print("----------------")
acqum <- mean(acqu);
acunm <- mean(acun);
print(acqum);
print("Brier Score")
pocosm<-mean(pocos,na.rm=T);
pocoum<-mean(pocou,na.rm=T);
print(pocosm);
print("Percentage on correct option")
hitm <- mean(hit,na.rm=T);
print(hitm);
print("Hit rate") ## Also compare to pocoum.

print("\\nRun inside R to access tables for plotting.")
