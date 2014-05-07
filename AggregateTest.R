th<-read.csv("...trade_history_report.csv")
tha<-read.csv("...trade_history_report2014-02-21T12_46_03.csv")

pit <- th$user_id; cat <- as.POSIXct(th$traded_at)
start <- as.POSIXct("2013-12-02 00:00:00 EST"); days <- seq(1,ceiling(as.double(Sys.time()-60*60*24 - start)),1)
np <- nt <- numeric()
for (d in 1:max(days)) {
 np[d] <- length(unique(pit[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24]))
 nt[d] <- length(cat[cat>=start+(d-1)*60*60*24&cat<start+d*60*60*24])
}
np.m <- mean(np)

temp <-as.vector(tha$num_trades); npm <- as.double(temp[length(temp)-1]); nta <- as.double(temp[1:(length(temp)-6)])

npm-np.m
npm-sum(np)/(length(np)-2)

length(nta)-length(nt)