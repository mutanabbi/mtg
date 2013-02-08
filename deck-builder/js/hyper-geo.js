/*
Population size N
Subpopulation size m
Sample size n
x value
*/
function hyp(x, n, m, nn) {
  var nz = m < n ? m : n;
  var mz = m < n ? n : m
  var h = 1, s = 1, k = 0, i = 0;
  while (i < x) {
    while ((s > 1) && (k < nz)) {
      h *= 1 - mz / (nn - k);
      s *= 1 - mz / (nn - k);
      ++k;
    }
    h *= (nz - i) * (mz - i) / (i + 1) / (nn - nz - mz + i + 1);
    s += h;
    ++i;
  }
  while (k < nz) {
    s *= 1 - mz / (nn - k);
    ++k;
  }
  return s;
}

function compute(form) {
  var Prob;
  var nn = Math.floor(eval(form.pop1.value));
  var m = Math.floor(eval(form.pop2.value));
  var n = Math.floor(eval(form.sample.value));
  var x = Math.floor(eval(form.argument.value));
  if ((n <= 0) || (m <= 0) || (nn <= 0)) {
    alert("Parameters must be positive integers");
    Prob = 0
  }
  else if ((m > nn) || (n > nn)) {
    alert("m and n must be less than N");
    Prob = 0
  }
  else if ((x < 0) || (x < n + m - nn))
    Prob = 0;
  else if ((x >= n) || (x >= m))
    Prob = 1;
  else {
    if (2 * m > nn) {
      if (2 * n > nn)
        Prob = hyp(nn - m - n + x, nn - n, nn - m, nn);
      else
        Prob = 1 - hyp(n - x - 1, n, nn - m, nn);
    }
    else if (2 * n > nn)
      Prob = 1 - hyp(m - x - 1, m, nn - n, nn)
    else
      Prob = hyp(x, n, m, nn)
  }
  Prob = Math.round(Prob * 100000) / 100000;
  form.result.value = Prob;
}