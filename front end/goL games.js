var games ={// list of sample games.
	Planes:(function(){
		var r = [
			[ ,1,1,1,0],
			[1, , ,1,0],
			[1, , , ,0],
			[1,1,1, ,0]]; 
		var ret = d3.range(0,64).map(function(y){ return d3.range(0,128).map(function(x){ return 0;})});
		//make four copies of r.
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[y+26][x+40]=(r[y][x]==undefined ? 0: r[y][x]); })});
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[32-y][60-x]=(r[y][x]==undefined ? 0: r[y][x]); })});
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[39-x][47+y]=(r[y][x]==undefined ? 0: r[y][x]); })});
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[19+x][53-y]=(r[y][x]==undefined ? 0: r[y][x]); })});
		return ret;
		return ret;
	}()),
	"Symm 4":(function(){
		var r = [
			[ ,1,1,1,0],
			[1, , ,1,0],
			[1, , , ,0],
			[1,1,1, ,0]]; 
		var ret = d3.range(0,64).map(function(y){ return d3.range(0,128).map(function(x){ return 0;})});
		//make four copies of r.
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[y+26][x+40]=(r[y][x]==undefined ? 0: r[y][x]); })});
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[32-y][60-x]=(r[y][x]==undefined ? 0: r[y][x]); })});
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[39-x][47+y]=(r[y][x]==undefined ? 0: r[y][x]); })});
		d3.range(0,r.length).forEach(function(y){d3.range(0,r[0].length)
			.forEach(function(x){ ret[19+x][53-y]=(r[y][x]==undefined ? 0: r[y][x]); })});
		return ret;
	}())
}