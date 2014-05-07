#Desired Stats and Graphs in order of coding priority:							#
# Timing on monthly reports?

# n trades per day graphed over days									#
#  n conditional trades per day graphed over days							#
#  n trades per question per day graphed over days							#
#  n trades per user per day graphed over days								#
#  n questions open per day graphed over days								NEED DATE POSTED
# n questions active (traded or commented) per day graphed over days
# n questions active per category per week graphed over weeks
# n users logged in per week graphed over weeks								NO LOGIN DATA!
# retention graph in the style of Ken
# n new users
# n users who haven't been active for more than x weeks
# n comments per day graphed over days									#
# cumulative Brier score (averaged over days) from nightly snapshot
# BS distribution (0 to 2) over questions per week graphed over weeks
#  dashes? or box and whisker?
#  BS distribution over questions per category
#  BS distribution over questions per question type
#  BS distribution over questions per duration of question (artificial categories)
#  BS distribution over questions per time to resolution (artificial categories)
# Hit rate (for binary and multi questions) per week graphed over weeks
# Expected BS over weeks
# Calibration according to various biases

# What about demographics? and other Study 2.3 items?

# distribution of trades per user for specified time frame as graph of user rank v. n trades
# distribution of score per user for specified time frame as graph of user rank v. SciCash
# distribution of trades per question for specified time frame as graph of question rank v. n trades

# n extant links
# n extant links per week graphed over weeks
# n links per open question

#
# Pull csv files from datamart.
# e.g., datamart.scicast.org/trade_history/?format=csv&api_key=XXXXXXX
#
# Read  files pulled from DataMart.

setwd("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3")
#library(rjson)
th<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/trade_history_report.csv")
#jth<- fromJSON(readLines("http://datamart.scicast.org/trade_history/?format=json&api_key=XXXXXXX"))
# th <- array(unlist(jth),c(9,length(jth)))											# 3 empty variables
qh<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/question_history_report.csv")
#jqh<- fromJSON(readLines("http://datamart.scicast.org/question_history/?format=json&api_key=XXXXXXX"))
# qh <- array(unlist(jqh),c(3,length(jqh)))
qn<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/question_report.csv")
#jqn<- fromJSON(readLines("http://datamart.scicast.org/question/?format=json&api_key=XXXXXXX"))
# qn <- array(unlist(jqn),c(24,length(jqn)))
 cm<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/comment_report.csv")
#jcm<- fromJSON(readLines("http://datamart.scicast.org/comment/?format=json&api_key=XXXXXXX"))
# cm <- array(unlist(jcm),c(8,length(jcm)))											# 2 empty variables
pr<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/person_report.csv")
#jpr<- fromJSON(readLines("http://datamart.scicast.org/person/?format=json&api_key=XXXXXXX"))
# pr <- array(unlist(jpr),c(13,length(jpr)))

des<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/demographic_survey.csv")
prs<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/profession_survey.csv")
pss<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/psychology_survey.csv")
sks<-read.csv("C:/Users/kolson8/Documents/Psychology/Prediction Market/Y3/skill_survey.csv")

ps1 <- merge(des,prs,by="Custom.Data",all=T); ps2 <- merge(pss,sks,by="Custom.Data",all=T)
prsnl <- merge(ps1,ps2,by="Custom.Data",all=T)

#
# Survey data
sid <- prsnl$Custom.Data; gn <- prsnl$What.is.your.gender.; ag <- prsnl$How.old.are.you.; oc1a <- prsnl$What.is.your.primary.occupation.;
oc1b <- prsnl$X.y; oc2a <- prsnl$What.additional.occupations.have.you.had.; oc2b <- prsnl$X.1.y; expt <- prsnl$In.what.additional.field.s..do.you.have.a.specialty.or.expertise.
pip <- pr$id; pac <- pr$num_trades; us <- pr$username; ac <- rep(0,length(sid))
for (i in 1:length(sid)) {
if (as.character(sid[i])%in%us) {
  ac[i] <- pac[us==as.character(sid[i])]
 }
}

cn <- c("user","gender","age","occupation1a","oc1b","oc2a","oc2b","expertise","trades")
write.table(data.frame(sid,gn,ag,oc1a,oc1b,oc2a,oc2b,expt,ac),file="personstats.csv",sep=",",append=F,col.names=cn,row.names=F)

#
# Checking on Study 2.1 participants

qit <- th$question_id; pit <- th$user_id
qiq <- qn$id; qr <- qn$roles
pir <- pr$roles
estart <- as.POSIXct("2014-02-21 01:00:00 EST"); edas <- ceiling(as.double(Sys.time()-60*60*24 - estart))
pie <- pip[pir=="Study 2.1A"|pir=="Study 2.1B"]
ea <- qiq[qr=="Study 2.1A"]; eb <- qiq[qr=="Study 2.1B"]; neq <- (length(ea)+length(eb))/2
eqac <- rep(0,length(pie)) # portion of questions in experiment that a person has edited at least once
etpd <- eqac # avg number of trades on experiment questions per day
o1a <- o1b <- o2a <- o2b <- xpt <- numeric()
for (i in 1:length(pie)) {
 use[i] <- us[pip==pie[i]]
 eqac[i] <- length(qit[pit==pie[i]&(qit%in%ea|qit%in%eb)])/neq
 etpd[i] <- length(unique(qit[pit==pie[i]&(qit%in%ea|qit%in%eb)]))/edas
 if (us[pip==pie[i]]%in%sid) {
  o1a[i] <- oc1a[sid==us[pip==pie[i]]]; o1b[i] <- oc1b[sid==us[pip==pie[i]]]; o2a[i] <- oc2a[sid==us[pip==pie[i]]]; o2b[i] <- oc2b[sid==us[pip==pie[i]]]; xpt[i] <- expt[sid==us[pip==pie[i]]]
 }
}
cn <- c("user","id","traded_questions","trades_per_day"occupation1a","oc1b","oc2a","oc2b","expertise")
write.table(data.frame(pie,use,eqac,etpd,o1a,o1b,o2a,o2b,xpt),file="participantstats.csv",sep=",",append=F,col.names=c("user","trades"),row.names=F)

# My own smoothing function!
smth <- function(x) {y<-x; for (i in 3:(length(x)-2)) { y[i] <- x[i-2]*0.1+x[i-1]*0.2+x[i]*0.4+x[i+1]*0.2+x[i+2]*0.1}; return(y)}

#
# Comments per day graph
cac <- as.POSIXct(cm$created_at); qic <- cm$question_id
#cac <- as.POSIXct(cm[6,,],format="%Y-%m-%dT%H:%M:%S"); qic <- cm[8,,]
start <- as.POSIXct("2013-11-25 01:00:00 EST")
days <- seq(1,ceiling(as.double(Sys.time()-60*60*24 - start)),1)
label <- as.character(c(25:30,"Dec 1",2:31,"Jan 1",2:31,"Feb 1",2:28))
nc <- numeric()
for (d in 1:max(days)) {
 nc[d] <- length(cac[cac>=start+(d-1)*60*60*24&cac<start+d*60*60*24])
}

png("CpD.png", width = 7200, height = 3600, pointsize = 18, res = 360)
par(mar=c(5,4,4,4))
plot(days,nc,type="l",lwd=3,xaxt="n",ylim=c(0,max(nc)*1.25),ylab="Comments per Day",xlab="Date")
 par(las=2)
 axis(1,at=days,lab=label[1:length(days)])
dev.off()

#
# Trades per day graph
cat <- as.POSIXct(th$traded_at)
#cat <- as.POSIXct(th[ ],format="%Y-%m-%dT%H:%M:%S")
start <- as.POSIXct("2013-11-25 01:00:00 EST")
#days <- seq(1,ceiling(as.double(Sys.time()-60*60*24 - start)),1)
label <- as.character(c(25:30,"Dec 1",2:31,"Jan 1",2:31,"Feb 1",2:28))
nt <- numeric()
for (d in 1:max(days)) {
 nt[d] <- length(cat[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])
}

png("TpD.png", width = 7200, height = 3600, pointsize = 18, res = 360)
par(mar=c(5,4,4,4))
plot(days,nt,type="l",lwd=3,xaxt="n",ylim=c(0,max(nt)*1.25),ylab="Trades per Day",xlab="Date")
 par(las=2)
 axis(1,at=days,lab=label[1:length(days)])
dev.off()

#
# Activity per question per day graph

qit <- th$question_id
#cat <- as.POSIXct(th$created_at)
#start <- as.POSIXct("2013-11-30 00:00:00 EST")
#days <- seq(1,ceiling(as.double(Sys.time() - start)),1)
#label <- as.character(c(25:30,"Dec 1",2:31,"Jan 1",2:31))
nt.q <- nc.q <- qu <- numeric()
for (d in 1:max(days)) {
# nt[d] <- length(cat[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])
 qu[d] <- length(levels(factor(c(qit[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24],qic[cac>=start+(d-1)*60*60*24&cac<start+d*60*60*24]))))
 if (qu[d] > 0) {
  nt.q[d] <- nt[d]/qu[d]; nc.q[d] <- nc[d]/qu[d]
 }
 else {nt.q[d] <- nc.q[d] <- 0}
}

qiqh <- qh$question_id; st <- as.POSIXct(qh$sample_time)
#qiqh <- qh[3,]; st <- as.POSIXct(qh[2,],format="%Y-%m-%dT%H:%M:%S")
nq <- numeric()
for (d in 1:max(days)) {
 nq[d] <- length(levels(factor(qiqh[st>=start+(d-1)*60*60*24&st<start+d*60*60*24])))
} 

png("ApQpD.png", width = 7200, height = 3600, pointsize = 18, res = 360)
par(mar=c(5,4,4,4))
plot(days,nt.q,type="l",lwd=1,col=rgb(0.99,0.6,0.6),xaxt="n",ylim=c(0,ceiling(max(nq)^(1/2))),ylab="",xlab="Date")
  lines(smooth.spline(days,smth(nt.q),df=ceiling(length(qu)/3),all.knots=T),lwd=3,col=rgb(0.95,0,0))
 lines(days,nc.q,lty=2,lwd=1,col=rgb(0.99,0.6,0.6))
  lines(smooth.spline(days,smth(nc.q),df=ceiling(length(qu)/3),all.knots=T),lty=2,lwd=3,col=rgb(0.95,0,0))
 lines(days,qu^(1/2),lwd=1,col=rgb(0.6,0.6,1))
  lines(smooth.spline(days,smth(qu^(1/2)),df=ceiling(length(qu)/3),all.knots=T),lwd=3,col=rgb(0,0,1))
 lines(days,nq^(1/2),lty=2,lwd=1,col=rgb(0.6,0.6,1))
  lines(smooth.spline(days,smth(nq^(1/2)),df=ceiling(length(qu)/3),all.knots=T),lty=2,lwd=3,col=rgb(0,0,1))
 mtext("Activity per Day", outer=T,side=2,line=-1.5,font=1,col=rgb(0.95,0,0))
 par(las=2)
 axis(1,at=days,lab=label[1:length(days)])
 axis(4,at=seq(0,ceiling(max(nq)^(1/2)),2),lab=seq(0,ceiling(max(nq)^(1/2)),2)^2)
 par(las=0)
 mtext("Questions per Day", outer=T,side=4,line=-1.5,font=1,col=rgb(0,0,1))
 text(18,10,"Open Questions",col=rgb(0,0,1),cex=0.9)
 text(18,6,"Active Questions",col=rgb(0,0,1),cex=0.9)
 text(18,0.75,"Trades per Active Question",col=rgb(0.95,0,0),cex=0.9)
 text(18,-0.25,"Comments per Active Question",col=rgb(0.95,0,0),cex=0.9)
dev.off()

#
# Conditional trades per day

as <- th$serialized_assumptions									# Conditions set on trades
qit <- th$question_id										# Question ID
qiq <- qn$id
ls <- qn$relationships_source_question_id; ld <- qn$relationships_destination_question_id							
rq <- qiq[is.na(ld)==F]										# Linked questions
#rq <- unique(qit[as!="None"])									# Older Linked questions
ptc <- length(qit[as!="None"])/length(qit[qit%in%rq])						# Portion of Conditional trades on eligible questions

#qiqh <- qh$question_id; st <- as.POSIXct(qh$sample_time)
nq <- nrq <- numeric(); ntc <- rep(0,length(days))
for (d in 1:max(days)) {
 nq[d] <- length(levels(factor(qiqh[st>=start+(d-1)*60*60*24&st<start+d*60*60*24])))
 nrq[d] <-length(levels(factor(qiqh[qiqh%in%rq&st>=start+(d-1)*60*60*24&st<start+d*60*60*24])))	# Number of linked questions
 ntc[d] <-length(qit[as!="None"&cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])		# Number of conditional trades on eligible questions
# if (nrq[d]>0) {
#  ntc[d] <-length(qit[as!="None"&cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])/nrq[d]	# Portion of conditional trades on eligible questions
# }										
}

png("CTpD.png", width = 7200, height = 3600, pointsize = 18, res = 360)
par(mar=c(5,4,4,4))
plot(days,ntc,type="l",lwd=1,col=rgb(0.99,0.6,0.6),xaxt="n",ylim=c(0,ceiling(max(nq)/6)),ylab="",xlab="Date")
  lines(smooth.spline(days,smth(ntc),df=ceiling(length(ntc)/2),all.knots=T),lwd=3,col=rgb(0.95,0,0))
 lines(days,nrq/6,lwd=1,col=rgb(0.6,0.6,1))
  lines(smooth.spline(days,smth(nrq/6),df=ceiling(length(ntc)/3),all.knots=T),lwd=3,col=rgb(0,0,1))
 lines(days,nq/6,lty=2,lwd=1,col=rgb(0.6,0.6,1))
  lines(smooth.spline(days,smth(nq/6),df=ceiling(length(ntc)/3),all.knots=T),lty=2,lwd=3,col=rgb(0,0,1))
 mtext("Trades per Day", outer=T,side=2,line=-1.5,font=1,col=rgb(0.95,0,0))
 par(las=2)
 axis(1,at=days,lab=label[1:length(days)])
 axis(4,at=seq(0,ceiling(max(nq)/6),10),lab=seq(0,ceiling(max(nq)/6),10)*6)
 par(las=0)
 mtext("Questions per Day", outer=T,side=4,line=-1.5,font=1,col=rgb(0,0,1))
 text(20,30,"Open Questions",col=rgb(0,0,1),cex=0.9)
 text(20,12,"Linked Questions",col=rgb(0,0,1),cex=0.9)
 text(20,6,"Conditional Trades on Linked Questions",col=rgb(0.95,0,0),cex=0.9)
dev.off()

#
# Questions active per category per week graph
weeks <- seq(1,ceiling(as.double(Sys.time()-60*60*24 - start)/7),1)
#qiq <- qh$question_id; st <- as.POSIXct(qh$sample_time)
#nq <- numeric()
ct <- qn$categories; qiq <- qn$id; wt <- rep(0,length(qiq)); cg <- array(numeric(), c(length(qiq),18))
for (j in 1:length(qiq)) {
 temp <- levels(factor(strsplit(as.character(ct[j]),",")[[1]]))
 wt[j]<-1/length(temp); cg[j,1:(length(temp))]<- temp
}
ac <- levels(factor(as.vector(cg)))
nq.c <- array(rep(0,length(ac)*max(weeks)),c(length(ac),max(weeks)))
for (w in 1:max(weeks)) {
 temp <- unique(qiqh[st>=start+(w-1)*60*60*24*7&st<start+w*60*60*24*7])
 cw <-numeric(); oc <-array(rep(NA,length(temp)*18),c(length(temp),18))
 if (length(temp)>0) {
  for (j in 1:length(temp)) {
   cw[j]<-wt[qiq==temp[j]]; oc[j,]<-cg[qiq==temp[j]]
  }
 }
 for (i in 1:length(ac)) {
  if (length(oc[oc==ac[i]&is.na(oc)==F])>0) {
   nq.c[i,w] <- sum(cw[which(oc==ac[i],arr.ind=T)[,1]])
  }
 }
}
nq.c.stack <- aperm(t(apply(aperm(nq.c), 1, cumsum)))

png("QpCpW.png", width = 7200, height = 3600, pointsize = 18, res = 360)
par(mar=c(5,4,4,4))
plot(weeks,nq.c.stack[1,],type="l",lwd=1,col=rgb(0.2,0.2,0.2),ylim=c(0,max(nq.c.stack)*1.05),ylab="Questions per Week",xlab="Week")
 text(3.5,nq.c.stack[1,4]/2,ac[i],col=rgb(0.2,0.2,0.2),cex=0.7)
# par(las=2)
# axis(1,at=weeks)
for (i in 2:length(ac)) {
 color<-rgb(rbeta(1,1.5,1.5)*0.85,rbeta(1,1.5,1.5)*0.85,rbeta(1,1.5,1.5)*0.85)
 lines(weeks,nq.c.stack[i,],lwd=1,col=color)
 par(las=0)
 text(3.5,sum(nq.c.stack[(i-1):i,4])/2,ac[i],col=color,cex=0.7)
}
dev.off()

#
# Trades per person per day graph

cap <- as.POSIXct(pr$created_at); pip <- pr$id; pit <- th$user_id
np <- nt.p <- pu <- numeric()
for (d in 1:max(days)) {
# nt[d] <- length(cat[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])
 pu[d] <- length(levels(factor(pit[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])))
 np[d] <- length(pip[cap<start+d*60*60*24])
 if (pu[d]>0) {
  nt.p[d] <- nt[d]/pu[d]
 }
 else {nt.p[d] <- 0}
} 

png("TpPpD.png", width = 7200, height = 3600, pointsize = 18, res = 360)
par(mar=c(5,4,4,4))
plot(days,nt.p,type="l",lwd=1,col=rgb(0.99,0.6,0.6),xaxt="n",ylim=c(0,ceiling((max(np)^(1/3)))),ylab="",xlab="Date")
  lines(smooth.spline(days,smth(nt.p),df=ceiling(length(nt.p)/3),all.knots=T),lwd=3,col=rgb(0.95,0,0))
 lines(days,pu^(1/3),lwd=1,col=rgb(0.6,0.6,1))
  lines(smooth.spline(days,smth(pu^(1/3)),df=ceiling(length(pu)/3),all.knots=T),lwd=3,col=rgb(0,0,1))
 lines(days,np^(1/3),lty=2,lwd=1,col=rgb(0.6,0.6,1))
  lines(smooth.spline(days,smth(np^(1/3)),df=ceiling(length(np)/2),all.knots=T),lty=2,lwd=3,col=rgb(0,0,1))
 mtext("Trades per Day", outer=T,side=2,line=-1.5,font=1,col=rgb(0.95,0,0))
 par(las=2)
 axis(1,at=days,lab=label[1:length(days)])
 axis(4,at=seq(0,ceiling((max(np)^(1/3))),1),lab=(seq(0,ceiling((max(np)^(1/3))),1))^3)
 par(las=0)
 mtext("Users per Day", outer=T,side=4,line=-1.5,font=1,col=rgb(0,0,1))
 text(26,4.5,"Trades per Active User",col=rgb(0.95,0,0))
 text(26,1,"Active Users",col=rgb(0,0,1))
 text(26,7,"All Users",col=rgb(0,0,1))
dev.off()

#
# Trades per question
tq <- numeric()
for (i in 1:length(qiq)) {
 tq[i] <- length(qit[qit==qiq[i]])
}

png("TpQ.png", width = 7200, height = 3600, pointsize = 18, res = 360)
plot(qiq,tq,pch=16,col=rgb(0,0,1),ylab="Number of Trades",xaxt="n",xlab="Question ID")
 axis(1,at=seq(10,max(qiq),10))
dev.off()
