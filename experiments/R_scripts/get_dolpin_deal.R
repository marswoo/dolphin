##########################
#prepare
#获取dolphin历史成交信息：id timestamp	is_buy	stockid	price	amount	is_real
##########################
library(RMySQL)
conn <- dbConnect(MySQL(), dbname = "tf2", username="root", password="")

##########################
#process
##########################
res <- dbGetQuery(conn, "select * from dolphin_deal where is_real = 1 order by stockid;")
res_0<-res[which(res["is_buy"]==0),]
res_1<-res[which(res["is_buy"]==1),]
result<-data.frame(colnames=t(colnames(res)))

for (i in 1:length(res_0[,1])){
  t0 <- strptime(res_0[i,2], "%Y-%m-%d %H:%M:%S")
  stockid0 <- res_0[i,4]
  t1_index <- which(strptime(res_1[,2], "%Y-%m-%d %H:%M:%S") > t0 & res_1[,4] == stockid0)[1]
  if (is.na(t1_index) & is.na(res_1[t1_index,]["id"])){
    next
  }
  result<-t(data.frame(t(result),t(as.vector(res_0[i,]))))
  result<-t(data.frame(t(result),t(as.vector(res_1[t1_index,]))))
}

result <- data.frame(result, row.names=c(1:length(result[,1])))
write.table(result, "output/dolphin_deal.txt")

##########################
#end
##########################
dbDisconnect(conn)