public class User implements Comparable<Object> {

	private String ipaddr, username, lat, lon, city, state, country, email,
			name;
	private int trades90, trades30, tradesweek, userid, numLogins;

	public User() {

	}

	public User(String[] temp, int[] location) {
		// location: [0]>id [1]>username [2]>trades90 [3]>trades30
		// [4]>tradesweek [5]>email
		// for(String x:temp)
		// System.out.print(x+" ");
		for (int y : location) {
			if(y == -1)
				geolocate.log("Location variable not found", new Exception());
		}
		setUserid(Integer.parseInt(temp[location[0]]));
		setUsername(temp[location[1]]);
		setTrades90(Integer.parseInt(temp[location[2]]));
		setTrades30(Integer.parseInt(temp[location[3]]));
		setTradesweek(Integer.parseInt(temp[location[4]]));
		setEmail(temp[location[5]]);
		String firstname = temp[location[6]];
		String lastname = temp[location[7]];
		setName(firstname + " " + lastname);
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
		return username.compareTo(tempUser.getUsername());
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

	public void setTrades90(int trades90) {
		this.trades90 = trades90;
	}

	public void setTrades30(int trades30) {
		this.trades30 = trades30;
	}

	public void setTradesweek(int tradesweek) {
		this.tradesweek = tradesweek;
	}

	public String getUsername() {
		return username;
	}

	public int getTrades90() {
		return trades90;
	}

	public int getTrades30() {
		return trades30;
	}

	public int getTradesweek() {
		return tradesweek;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public int getnumLogins() {
		return numLogins;
	}

	public void addTicket() {
		numLogins++;
	}

	public void setnumLogins(int numLogins) {
		this.numLogins = numLogins;
	}

	@Override
	public String toString() {
		// IP,Username,Country,State,City,Latitude,Longitude,Trades 90, Trades
		// 30, Trades Week
		return this.getIpaddr() + "," + this.getUsername() + ","
				+ this.getCountry() + "," + this.getState() + ","
				+ this.getCity() + "," + this.getLat() + "," + this.getLon()
				+ "," + this.getTrades90() + "," + this.getTrades30() + ","
				+ this.getTradesweek();
	}

	public String dbString() {
		return this.getUserid() + "," + this.getUsername() + ","
				+ this.getEmail() + "," + this.getTrades90() + ","
				+ this.getTrades30() + "," + this.getTradesweek() + ","
				+ this.getnumLogins();
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

}
