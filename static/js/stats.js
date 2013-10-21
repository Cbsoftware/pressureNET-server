(function() {

    var global = this;

    var Stats = (global.Stats || (global.Stats = {}));

    Stats.nsort = function(vals) {
      return vals.sort(function (a, b) { return a - b })
    }

    Stats.sum = function(vals) {
      return vals.reduce(function (total, val) { return total + val }, 0)
    }

    Stats.mean = function(vals) {
      if (vals.length === 0) return NaN
      return (Stats.sum(vals) / vals.length)
    }

    Stats.median = function(vals) {
      if (vals.length === 0) return NaN

      var half = (vals.length / 2) | 0

      vals = Stats.nsort(vals)
      if (vals.length % 2) {
        // Odd length, true middle element
        return vals[half]
      }
      else {
        // Even length, average middle two elements
        return (vals[half-1] + vals[half]) / 2.0
      }
    }

    // Returns the mode of a unimodal dataset -- NaN for multi-modal or empty datasets.
    Stats.mode = function(vals) {
      if (vals.length === 0) return NaN
      var mode = NaN
      var dist = {}
      vals.forEach(function (n) {
        var me = dist[n] || 0
        me++
        dist[n] = me
      })
      var rank = Object.keys(dist).sort(function (a, b) { return dist[b] - dist[a] })
      mode = rank[0]
      if (dist[rank[1]] == dist[mode]) {
        // Multiple modes found, abort
        return NaN
      }
      return mode
    }

    // Variance = average squared deviation from mean
    Stats.variance = function(vals) {
      var avg = Stats.mean(vals)
      diff = vals.map(function (v) { return Math.pow((v - avg), 2) })
      return Stats.mean(diff)
    }

    // Standard Deviation = sqrt of variance
    Stats.stdev = function(vals) {
      return Math.sqrt(Stats.variance(vals))
    }

    Stats.percentile = function(vals, ptile) {
      if (vals.length === 0 || ptile == null || ptile < 0) return NaN

      // Fudge anything over 100 to 1.0
      if (ptile > 1) ptile = 1
      vals = Stats.nsort(vals)
      var i = (vals.length * ptile) - 0.5
      if ((i | 0) === i) return vals[i]
      // interpolated percentile -- using Estimation method
      var int_part = i | 0
      var fract = i - int_part
      return (1 - fract) * vals[int_part] + fract * vals[int_part + 1]
    }

    Stats.sigmoid = function(x) {
        return 1 / (1 + Math.exp(-x));
    }
}).call(this);
