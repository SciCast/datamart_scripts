# Change working directory.
setwd("C:/<YOURFAVORITEFOLDER>")
# Windows-specific internet connection
setInternet2(use = TRUE)
# Download and read file.
download.file("http://datamart.scicast.org/question/?format=csv&api_key=<YOURKEYHERE>",destfile="question_report.csv")
 qn<-read.csv("question_report.csv")

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

##############
# Selecting Study questions
##############

pisq <- qiq[grq=="Public"&ql=="False"&qv=="True"&saq==max(saq)&raq>as.POSIXct("2014-11-15 00:00:00 EST")&qps=="None"]

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
or <- order(tq[qiq%in%isq],cq[qiq%in%isq],raq[qiq%in%isq],ntq[qiq%in%isq])
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