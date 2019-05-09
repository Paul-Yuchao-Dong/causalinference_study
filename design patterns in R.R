fp <- function(f, x, converged, ...){
  value <- f(x, ...)
  if (converged(x, value)) value
  else Recall(f, value, converged, ...)
}

fpsqrt <- function(x, p) p/x

converged <- function(x, y) all(abs(x-y)<0.001)

averageDamp <- function(fun){
  function(x, ...) (x+fun(x, ...))/2
}

printValue <- function(fun) {
  function(x, ...) {
    cat(x, "\n")
    fun(x, ...)
  }
}

fqsqrt_cls <- function(p) {
  function(x) p / x
} 

nr <- function(X, y) {
  function(beta) beta - solve(-crossprod(X)) %*% crossprod(X, y - X %*% beta)
}

counterConst <- function(){
  # Constructor
  count <- 0
  function(){
    count <<- count + 1
    count
  }
}

counter <- local({
  count <- 0
  function(){
    count <<- count +1
    count
  }
})

addMaxIter <- function(converged, maxIter){
  count <- 0
  function(...){
    count <<- count + 1
    if (count>=maxIter) TRUE else converged(...)
  }
}
