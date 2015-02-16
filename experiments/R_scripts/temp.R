Sys.setenv("RODPS_CONFIG" = "/home/abc/odps_config.ini")
rodps.init("/home/abc/odps_config.ini")
library('RODPS')
tbl1 <- rodps.load.table('hitao_pvlog_tmp')
d <- head(tbl1)
x <- rodps.query('select * from hitao_pvlog_tmp limit 1000')
#sample
rodps.sample.srs('tbl1','small_tbl1',0.1 )

for (i in seq(from = 1, to = length(result[,1]), by = 2)){
  bp <- (result[i,5][[1]] - result[i, 12][[1]])/result[i, 12][[1]]
  endp <- result[i, 11][[1]]
  startp <- result[i+1, 10][[1]]
  sp <- (result[i+1, 5][[1]] - result[i+1, 12][[1]])/result[i+1, 12][[1]]
  print(c(result[i+1, 2][[1]], result[i+1, 4][[1]], bp, endp, startp, sp))
}