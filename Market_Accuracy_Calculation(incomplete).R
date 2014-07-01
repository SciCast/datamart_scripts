# Find resolved questions.
ctq <- qn$categories; orq <- qn$is_ordered; orq <- as.double(orq)
#rsq <- levels(factor(qiq[raq<=Sys.time()&caq>start]))
rsq <- levels(factor(qiq[raq<=Sys.time()&caq>start&ctq!="Study 2.1"&ctq!="Study 2.1,Study 2.1"]))
 frc <- numeric()
 for (q in 1:length(rsq)) {frc[q] <- length(tat[qit==rsq[q]])}								# Removing questions that have almost no forecasts
 rsq <- rsq[frc>1]
rvq <- qn$resolution_value_array; rvqat <- array(rep(-1,length(tat)*20),c(length(tat),20)); roqt <- rep(-1,length(tat))
for (t in 1:length(tat)) {
 temp <- as.double(strsplit(strsplit(strsplit(as.character(rvq[qiq==qit[t]]),"[",fixed=T)[[1]][2],"]",fixed=T)[[1]],",")[[1]])
 if (is.na(temp[1])==F) {
  rvqat[t,1:length(temp)] <- temp
  if (temp[1]%%1==0) {
   roqt[t] <- which(rvqat[t,]==1)-1
  }
 }
}
#tat <- as.POSIXct(th$traded_at); nvt <- th$new_value_list
# Weight forecasts by how long they endure. Average over questions.
acqu <- acun <- nfqu <- pocos <- pocou <- hit <- rep(2,length(rsq))
 base <- start-28*24*60*60
for (q in 1:length(rsq)) {
 time <- c(tat[qit==rsq[q]&asqt%in%c(-1,rsq)&(asot==roqt|asot==-1)],raq[qiq==rsq[q]]); or <- order(time); time <- time[or]
 lt <- length(time); nfqu[q] <- lt-1
  tmp1 <- as.double(strsplit(strsplit(strsplit(as.character(rvq[qiq==rsq[q]]),"[",fixed=T)[[1]][2],"]",fixed=T)[[1]],",")[[1]])
  ac <- acd <- act <- rep(2,lt); pocot <- hitt <- rep(0,lt)
# Pretend the first trade lasted 24 hours because we don't have a record of how long the questions were paused after being published.
   acd[1] <- time[1]-base -(time[1]-24*60*60-base)
   pocot[1] <- pocou[q] <- 1/length(tmp1)
   if (lt>1) {
    for (t in 1:(lt-1)) {
     acd[t+1] <- time[t+1]-base -(time[t]-base)
     tmp2 <- as.double(strsplit(as.vector(nvt[qit==rsq[q]&asqt%in%c(-1,rsq)&(asot==roqt|asot==-1)])[or[t]],",")[[1]])
     b <- which(tmp1==max(tmp1))
     pocot[t+1] <- tmp2[b]
     if (mean(which(tmp2==max(tmp2)))==b) {hitt[t+1] <- 1};
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
    tmp2 <- as.double(strsplit(as.vector(nvt[qit==rsq[q]&asqt%in%c(-1,rsq)&(asot==roqt|asot==-1)])[or[t]],",")[[1]])
    actt <-rep(0,length(tmp1)-1)
    for (o in 1:(length(tmp1)-1)) {
     actt[o] <- 2*(sum(tmp2[1:o])-sum(tmp1[1:o]))^2
    }
    act[t+1] <- sum(actt)/(length(tmp1)-1)
   }
   }
  }
  if (orq[qiq==rsq[q]]==1) {
    act[1] <- acun[q] <- (length(tmp1)-1)*(1/length(tmp1))^2+(1-1/length(tmp1))^2
   if (lt>1) {
    for (t in 1:(lt-1)) {
     tmp2 <- as.double(strsplit(as.vector(nvt[qit==rsq[q]&asqt%in%c(-1,rsq)&(asot==roqt|asot==-1)])[or[t]],",")[[1]])
     act[t+1] <- sum( (tmp2-tmp1)^2 )
    }
   }
  }
  acqu[q] <- sum(act*acd)/sum(acd)
  pocos[q] <-sum(pocot*acd)/sum(acd)
  hit[q] <- sum(hitt*acd)/sum(acd)
}
acqum <- mean(acqu); acunm <- mean(acun)
win <- round(100*(length(acqu[acqu<acun])/length(acqu)))
pocosm<-mean(pocos); pocoum<-mean(pocou)
hitm <- mean(hit) # Also compare to pocoum.

br <- seq(0,2,0.1)
png("AcpQ.png", width = 3600, height = 3600, pointsize = 18, res = 360)
one <- hist(acqu,breaks=br)
two <- hist(acun,breaks=br)
plot(two,col=rgb(0,0,1,0.5),xlim=c(0,2),xlab="Brier Score",ylab="Number of Questions",cex.main=1,main=paste("Accuracy through ",nowish,sep=""))
plot(one,col=rgb(1,0,0,0.5),add=T)
 text(0.8,17,pos=4,"Uniform Distribution of Forecasts",col=rgb(0,0,1,0.6))
 text(0.8,15,pos=4,"SciCast Forecasts",col=rgb(1,0,0,0.6))
 mtext(paste('        Scicast better on ',win,'% of questions',sep=''), outer=T,side=3,line=-4.5,cex=0.75,font=1,col=rgb(0,0,0,1))
 mtext('        based on "de-stuttered" forecasts weighted by how long they lasts', outer=T,side=3,line=-3.5,cex=0.75,font=1,col=rgb(0,0,0,1))
dev.off()
