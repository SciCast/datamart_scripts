public class User implements Comparable<Object> {

	private String ipaddr, username, lat, lon, city, state, country, email,
			name;
	private int trades30, trades90, tradesweek, userid, Accumulation,
			numLogins;

	public int getNumLogins() {
		return numLogins;
	}

	public void setNumLogins(int numLogins) {
		this.numLogins = numLogins;
	}

	public User() {

	}

	public User(int id, String user, String email, int accum, String newName,
			String type) {
		setUserid(id);
		setUsername(user);
		setEmail(email);
		if(type.equals("trades90"))
			this.setTrades90(accum);
		else if(type.equals("trades30"))
			this.setTrades30(accum);
		else if(type.equals("tradesweek"))
			this.setTradesweek(accum);
		else
			this.setNumLogins(accum);
		setName(newName);
	}

	public User(String[] temp, int[] location) {
		// location: [0]>id [1]>username [2]>trades90 [3]>trades30
		// [4]>tradesweek [5]>email
		// for(String x:temp)
		// System.out.print(x+" ");
		for (int y : location) {
			if(y == -1)
				getWinners.log("Location variable not found", new Exception());
		}
		setUserid(Integer.parseInt(temp[location[0]]));
		setUsername(temp[location[1]]);
		setTrades30(Integer.parseInt(temp[location[3]]));
		setEmail(temp[location[5]]);
		// System.out.println("userid: "+temp[location[0]]+" username: "+temp[location[1]]+" 90: "+temp[location[3]]+" 30: "+temp[location[4]]+" 7: "+temp[location[4]]);
	}

	public User(String IP, int ID) {
		ipaddr = IP;
		userid = ID;
	}

	public String getLat() {
		return lat;
	}

	@Override
	public boolean equals(Object obj) {
		User tempUser = (User) obj;
		return userid == tempUser.getUserid();
	}

	@Override
	public int compareTo(Object o) {
		User tempUser = (User) o;
		return username.compareToIgnoreCase(tempUser.getUsername());
	}

	public void setLat(String lat) {
		this.lat = lat;
	}

	public String getLon() {
		return lon;
	}

	public void setLon(String lon) {
		this.lon = lon;
	}

	public String getCity() {
		return city;
	}

	public void setCity(String city) {
		this.city = city;
	}

	public String getState() {
		return state;
	}

	public void setState(String state) {
		this.state = state;
	}

	public String getCountry() {
		return country;
	}

	public void setCountry(String country) {
		this.country = country;
	}

	public int getUserid() {
		return userid;
	}

	public void setUserid(int userid) {
		this.userid = userid;
	}

	public String getIpaddr() {
		return ipaddr;
	}

	public void setIpaddr(String ipaddr) {
		this.ipaddr = ipaddr;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public void setTrades30(int trades30) {
		this.trades30 = trades30;
	}

	public String getUsername() {
		return username;
	}

	public int getTrades30() {
		return trades30;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public int getTrades90() {
		return trades90;
	}

	public void setTrades90(int trades90) {
		this.trades90 = trades90;
	}

	public int getTradesweek() {
		return tradesweek;
	}

	public void setTradesweek(int tradesweek) {
		this.tradesweek = tradesweek;
	}

	public int getAccumulation() {
		return Accumulation;
	}

	public void setAccumulation(int Accumulation) {
		this.Accumulation = Accumulation;
	}

	@Override
	public String toString() {
		// IP,Username,Country,State,City,Latitude,Longitude,Trades 90, Trades
		// 30, Trades Week
		return this.getUserid() + "," + this.getUsername() + ","
				+ this.getAccumulation();
	}

	public void resetAccumulation() {
		setAccumulation(0);

	}

	public void addAccumulation(String type, int val) {
		if(type.equals("trades90")) {
			int temp = this.getTrades90();
			temp += val;
			this.setTrades90(temp);
		}
		else if(type.equals("trades30")) {
			int temp = this.getTrades30();
			temp += val;
			this.setTrades30(temp);
		}
		else if(type.equals("tradesweek")) {
			int temp = this.getTradesweek();
			temp += val;
			this.setTradesweek(temp);
		}
		else {
			int temp = this.getNumLogins();
			temp += val;
			this.setNumLogins(temp);
		}
	}

	public void addAccumulation(String type) {
		int temp = this.getAccumulation();
		if(type.equals("trades90"))
			temp += this.getTrades90();
		else if(type.equals("trades30"))
			temp += this.getTrades30();
		else if(type.equals("tradesweek"))
			temp += this.getTradesweek();
		else
			temp += this.getNumLogins();
		this.setAccumulation(temp);
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

}
