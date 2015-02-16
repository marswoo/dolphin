##########################
#prepare
#获取dolphin历史成交信息：id timestamp	is_buy	stockid	price	amount	is_real，以及当天对应的max_delta, min_delta, start_delta, end_delta
##########################
library(RMySQL)
conn <- dbConnect(MySQL(), dbname = "tf2", username="root", password="")

getsql1 <- function(d, stockid){
  str <- paste("select max((current_price - yesterday_close_price)/yesterday_close_price) as max_delta,min((current_price - yesterday_close_price)/yesterday_close_price) as min_delta,max(time) as max_time,min(time) as min_time from dolphin_stockmetadata where date='", d, "' and stockid='", stockid, "'", sep = "")
  return(str)
}

getsql2 <- function(t, d, stockid){
  str <- paste("select (current_price - yesterday_close_price)/yesterday_close_price as delta, yesterday_close_price as yprice from dolphin_stockmetadata where date='", d, "' and stockid='", stockid, "' and time='", t, "' limit 1", sep = "")
  return(str)
}

getbasic <- function(ts, stockid){
  d <- strsplit(ts, " ")[[1]][1]
  sql1 <- getsql1(d, stockid)
  res_tmp <- dbGetQuery(conn, sql1)
  sql2 <- getsql2(res_tmp["max_time"], d, stockid)
  end_delta <- dbGetQuery(conn, sql2)
  if (length(end_delta) == 0){
    return (rep(NA,5)) #有交易，但是delta数据没有
  }

  yprice <- end_delta["yprice"]
  end_delta <- end_delta["delta"]

  sql2 <- getsql2(res_tmp["min_time"], d, stockid)
  start_delta <- dbGetQuery(conn, sql2)
  if (length(start_delta) == 0){
    return (rep(NA,5))
  }
  yprice <- start_delta["yprice"]
  start_delta <- start_delta["delta"]
  return (c(res_tmp["max_delta"], res_tmp["min_delta"], start_delta=start_delta["delta"], end_delta=end_delta["delta"], yprice=yprice["yprice"]))
}

##########################
#process
##########################
res <- dbGetQuery(conn, "select * from dolphin_deal where is_real = 1 order by stockid;")
res_0<-res[which(res["is_buy"]==0),]
res_1<-res[which(res["is_buy"]==1),]
result<-data.frame()

end <- length(res_0[,1])
for (i in 1:length(res_0[,1])){
#for (i in 1:10){
  print(c(i,end))
  t0 <- format(strptime(res_0[i,2], "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d")
  t1 <- format(strptime(res_1[,2], "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d")
  stockid0 <- res_0[i,4]
  
  s0basic <- getbasic(res_0[i,2], stockid0)
  
  if (is.na(s0basic)[1]){#没找到对应的delta数据
    print("-------")
    print("s0basic")
    print(res_0[i,2])
    print(stockid0)
    print("-------")
    next
  }
  
  t1_index <- which(t1 > t0 & res_1[,4] == stockid0)[1]
  if (is.na(t1_index) & is.na(res_1[t1_index,]["id"])){
    next
  }
  
  s1basic <- getbasic(res_1[t1_index,2], stockid0)
  if (is.na(s1basic)[1]){
    print("-------")
    print("s1basic")
    print(res_1[t1_index,2])
    print(stockid0)
    print("-------")
    next
  }
  
  item0 <- data.frame(res_0[i,], t(s0basic))
  item1 <- data.frame(res_1[t1_index,], t(s1basic))
  
  if (item0["stockid"][[1]] != item1["stockid"][[1]]){
    print("-------")
    print("item")
    print(item0)
    print(item1)
    print("-------")
    next
  }
  
  if (length(which(is.na(item0))) != 0){
    print("-------")
    print("item0")
    print(item0)
    print("-------")
    next
  }
  if (length(which(is.na(item1))) != 0){
    print("-------")
    print("item1")
    print(item1)
    print("-------")
    next
  }
  
  if (length(result) == 0){
    result <- item0
    result <- t(data.frame(t(result), t(item1)))
  }else{
    result <- t(data.frame(t(result), t(item0)))
    result <- t(data.frame(t(result), t(item1)))
  }  
}

write.table(result, "output/dolphin_deal.txt", sep = "\t")

##########################
#end
##########################
dbDisconnect(conn)

