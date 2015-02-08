##########################
#prepare
#获取每一支stock对应的stockid,pair,thr,thr_delta,delta_date,thr_delta_time,max_delta,min_delta,end_delta
##########################
#install.packages('RMySQL')
#install.packages("lubridate")
library(lubridate)
library(RMySQL)
conn <- dbConnect(MySQL(), dbname = "tf2", username="root", password="")

getsql <- function(stockid, date){
  sql = paste("select stockid, (current_price - yesterday_close_price)/yesterday_close_price as delta, time, date
      from dolphin_stockmetadata where stockid='", stockid, "' and date='", date, "'", sep="")
  #print(sql)
  return(sql)
}

pairs <- c(
  'sh600216_sz002001',
  'sz002136_sz002601',
  'sh600209_sz000735',
  'sh600389_sh600596',
  'sz002441_sz300068',
  'sh600884_sz002091',
  'sh600880_sz300052',
  'sh600597_sh600887',
  'sh600435_sh600501',
  'sh600031_sz000157',
  'sh600343_sh600879',
  'sz000568_sz000858',
  'sz002279_sz002474',
  'sh600030_sh600837',
  'sz000333_sz000651',
  'sh601601_sh601628',
  'sz000789_sz002233',
  'sz000877_sh600425', 
  'sz000001_sh601166', 
  'sh600011_sh600027', 
  'sz000758_sh601168', 
  'sz000088_sz000507',   
  'sh600875_sh601727',
  'sh600199_sh600702', 
  'sh600259_sz000831',
  'sh600026_sh601866',
  'sh600789_sz002166',
  'sh600648_sh600663', 
  'sh601801_sh601928',
  'sh600048_sz000024'
)

##########################
#process
##########################

output <- data.frame()
for (pair in pairs){
  print(paste("processing:", pair, now()))
  stockids <- strsplit(pair, "_")
  for (i in 1:length(stockids)){
    for (j in 1:length(stockids[[i]])){
      stockid <- stockids[[i]][j]
      beg_date <- ymd("20140501")
      end_date <- ymd("20150120")
      while(beg_date < end_date){
        res <- dbGetQuery(conn, getsql(stockid, beg_date))
 
        max_delta <- max(res$delta)
        min_delta <- min(res$delta)
        end_delta <- res[["delta"]][length(res[["delta"]])]
        for (thr in c(0.02,0.025,0.03,0.04)){
          thr_delta <- res[["delta"]][which(res[["delta"]] > thr)[1]]
          thr_delta_time <- res[["time"]][which(res[["delta"]] > thr)[1]]
          if (is.double(thr_delta) && !is.na(thr_delta)){
            delta_date <- strftime(beg_date, "%Y-%m-%d")
            if (length(output) == 0){
              output <- data.frame(stockid,pair,thr,thr_delta,delta_date,thr_delta_time,max_delta,min_delta,end_delta)
            }else{
              output <- t(data.frame(t(output), c(stockid,pair,thr,thr_delta,delta_date,thr_delta_time,max_delta,min_delta,end_delta)))
            }
          }
          
          thr <- -thr
          thr_delta <- res[["delta"]][which(res[["delta"]] < thr)[1]]
          thr_delta_time <- res[["time"]][which(res[["delta"]] < thr)[1]]
          if (is.double(thr_delta) && !is.na(thr_delta)){
            delta_date <- strftime(beg_date, "%Y-%m-%d")
            if (length(output) == 0){
              output <- data.frame(stockid,pair,thr,thr_delta,delta_date,thr_delta_time,max_delta,min_delta,end_delta)
            }else{
              output <- t(data.frame(t(output), c(stockid,pair,thr,thr_delta,delta_date,thr_delta_time,max_delta,min_delta,end_delta)))
            }
          }
        }
        beg_date <- beg_date + ddays(1)
      }
    }
  }
}
output <- data.frame(output, row.names=1:(length(output[,1])))
write.table(output, "output/stat_result.txt")

##########################
#end
##########################
dbDisconnect(conn)



