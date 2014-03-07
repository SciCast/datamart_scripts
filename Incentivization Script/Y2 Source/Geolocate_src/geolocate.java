import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.ListIterator;
import java.util.Map;

public class geolocate {

	public static String IPCSV = "ip_dump.csv";
	public static String USERCSV = "users.csv";
	public static String LOGFILE = "geolocate.log";
	public static String URL = "";
	public static int DELAY = 501;
	public static String CONFIG = "geolocate.cfg";
	public static String OUTPUT = "georesults.csv";
	public static String DB = "users.db";
	public static String THRINFO = "phpOutput";
	private static ArrayList<User> users = new ArrayList<User>();
	public static int DEBUG = 0;

	public static void main(String[] args) {
		if (args.length != 0) {
			if (args[0].length() == 1)
				DEBUG = Integer.parseInt(args[0]);
			else
				CONFIG = args[0];
		}
		File f = new File(CONFIG);
		if (f.exists()) {
			/* do something */
			try {
				// Open the file that is the first
				// command line parameter
				FileInputStream fstream = new FileInputStream(CONFIG);
				// Get the object of DataInputStream
				DataInputStream in = new DataInputStream(fstream);
				BufferedReader br = new BufferedReader(
						new InputStreamReader(in));
				String strLine;
				while ((strLine = br.readLine()) != null) {
					if (strLine.matches("(?i)^IPCSV:.+")) {
						String[] temp = strLine.split(":");
						if (temp[1].trim().length() != 0)
							IPCSV = temp[1].trim();
					} else if (strLine.matches("(?i)^LOGFILE:.+")) {
						String[] temp = strLine.split(":");
						if (temp[1].trim().length() != 0)
							LOGFILE = temp[1].trim();
					} else if (strLine.matches("(?i)^USERDB:.+")) {
						String[] temp = strLine.split(":");
						if (temp[1].trim().length() != 0)
							DB = temp[1].trim();
					} else if (strLine.matches("(?i)^URL:.+")) {
						String[] temp = strLine.split(":");
						if (temp[1].trim().length() != 0)
							URL = temp[1].trim() + ":" + temp[2].trim();
					} else if (strLine.matches("(?i)^GEOOUTPUT:.+")) {
						String[] temp = strLine.split(":");
						if (temp[1].trim().length() != 0)
							OUTPUT = temp[1].trim();
					} else if (strLine.matches("(?i)^DELAY:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							DELAY = Integer.parseInt(tempNum);
					} else if (strLine.matches("(?i)^USERCSV:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							USERCSV = tempNum;
					} else if (strLine.matches("(?i)^PHPOUTPUT:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							THRINFO = tempNum;
					}
				}
				in.close();
			} catch (Exception e) {
				log("Problem reading config file", new FileNotFoundException());
			}
		}
		try {
			// Open the file that is the first
			// command line parameter
			FileInputStream fstream = new FileInputStream(IPCSV);
			// Get the object of DataInputStream
			DataInputStream in = new DataInputStream(fstream);
			BufferedReader br = new BufferedReader(new InputStreamReader(in));
			String strLine;
			ArrayList<User> ipAddr = new ArrayList<User>();
			// Read File Line By Line
			strLine = br.readLine();
			int[] location = findIP(strLine);
			if (location[0] == -1) {
				log("IP address not in data", new Exception());
				in.close();
				System.exit(1);
			}
			Map<Integer, Integer> logins = new HashMap<Integer, Integer>();
			// Read File Line By Line
			strLine = br.readLine();
			while ((strLine = br.readLine()) != null) {
				String[] temp = strLine.split(",");
				boolean isBot = false;
				for (String x : temp) {
					if (x.matches("(?i).*java.*") || x.equalsIgnoreCase("2418")
							|| x.matches("(?i).*ping.*"))
						isBot = true;
				}
				if (temp[location[1]].equals("")
						|| temp[location[0]].equals(""))
					isBot = true;
				if (isBot)
					continue;
				else {
					User tempUser = new User(temp[location[0]],
							Integer.parseInt(temp[location[1]]));
					if (!ipAddr.contains(tempUser)) {
						ipAddr.add(tempUser);
						logins.put(tempUser.getUserid(), 1);
					} else {
						int tempID = logins.remove(tempUser.getUserid());
						tempID += 1;
						logins.put(tempUser.getUserid(), tempID);
					}
				}
			}
			// Close the input stream
			in.close();
			fstream = new FileInputStream(USERCSV);
			in = new DataInputStream(fstream);
			br = new BufferedReader(new InputStreamReader(in));
			strLine = br.readLine();
			int[] info = findInfo(strLine);
			while ((strLine = br.readLine()) != null) {
				String[] temp = strLine.split(",");
				boolean isBot = false;
				for (String x : temp) {
					if (x.equalsIgnoreCase("root@localhost")
							|| x.equalsIgnoreCase(""))
						isBot = true;
				}
				// if(Integer.parseInt(temp[info[2]]) == 0) isBot = true;
				if (isBot)
					continue;
				else {
					User tempUser = new User(temp, info);
					if (ipAddr.contains(tempUser)) {
						tempUser.setIpaddr(ipAddr.get(ipAddr.indexOf(tempUser))
								.getIpaddr());
						if (!users.contains(tempUser))
							users.add(tempUser);
					} else {
						continue;
						// log("User not found in IP database: "
						// + tempUser.getUsername(), new Exception());
						// System.exit(1);
					}
				}
			}
			in.close();

			ListIterator<User> it = users.listIterator();
			while (it.hasNext()) {
				User tempUser = it.next();
				if (logins.containsKey(tempUser.getUserid()))
					tempUser.setnumLogins(logins.get(tempUser.getUserid()));
			}
			if (DEBUG != 1)
				getCoords();
			fstream = new FileInputStream(THRINFO);
			in = new DataInputStream(fstream);
			br = new BufferedReader(new InputStreamReader(in));
			strLine = br.readLine();
			in.close();
			String[] temp = strLine.split("#");
			write(temp);
		} catch (Exception e) {// Catch exception if any
			log("File Not Found", e);
		}

	}

	private static int[] findInfo(String strLine) {
		String[] temp = strLine.split(",");
		int[] retval = { -1, -1, -1, -1, -1, -1, -1, -1 };
		int count = 0;
		for (String x : temp) {
			// location: [0]>id [1]>username [2]>trades90 [3]>trades30
			// [4]>tradesweek
			if (x.equalsIgnoreCase("user_id"))
				retval[0] = count;
			else if (x.equalsIgnoreCase("username"))
				retval[1] = count;
			else if (x.equalsIgnoreCase("traded_last_90"))
				retval[2] = count;
			else if (x.equalsIgnoreCase("traded_last_30"))
				retval[3] = count;
			else if (x.equalsIgnoreCase("traded_last_week"))
				retval[4] = count;
			else if (x.equalsIgnoreCase("email"))
				retval[5] = count;
			else if (x.equalsIgnoreCase("name_first"))
				retval[6] = count;
			else if (x.equalsIgnoreCase("name_last"))
				retval[7] = count;
			count++;
		}

		return retval;
	}

	private static int[] findIP(String strLine) {
		String[] temp = strLine.split(",");
		int[] retval = { -1, -1 };
		int count = -1;
		for (String x : temp) {
			count++;
			if (x.trim().equalsIgnoreCase("ip_addr"))
				retval[0] = count;
			else if (x.trim().equalsIgnoreCase("user_id"))
				retval[1] = count;
		}
		return retval;

	}

	protected static void log(String message, Exception e) {
		try {
			// Create file
			FileWriter fstream = new FileWriter(LOGFILE, true);
			BufferedWriter out = new BufferedWriter(fstream);
			Date current = new Date();
			String now = current.toString();
			if (DEBUG == 2)
				e.printStackTrace();
			String output = now + ": " + message + ": " + e + "\n";
			out.write(output);
			// Close the output stream
			out.close();
		} catch (Exception f) {// Catch exception if any
			System.err.println("Error: " + f.getMessage());
			f.printStackTrace();
		}
	}

	private static void write(String[] temp) {
		try {
			FileWriter fWriter = new FileWriter(OUTPUT);
			BufferedWriter out = new BufferedWriter(fWriter);
			out.write("IP,Username,Country,State,City,Latitude,Longitude,Trades 90,Trades30,Trades Week\n");
			ListIterator<User> it = users.listIterator();
			while (it.hasNext()) {
				User tempUser = it.next();
				out.write(tempUser + "\n");
			}
			out.close();
			fWriter = new FileWriter(DB);
			out = new BufferedWriter(fWriter);
			it = users.listIterator();
			out.write(temp[0] + "," + temp[1] + "\n");
			while (it.hasNext()) {
				User tempUser = it.next();
				if (tempUser.getEmail().matches(".*mercyhurst.*"))
					continue;
				if (temp.equals("trades90"))
					out.write(tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + ","
							+ tempUser.getTrades90() + "," + tempUser.getName()
							+ "\n");
				else if (temp.equals("trades30"))
					out.write(tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + ","
							+ tempUser.getTrades30() + "," + tempUser.getName()
							+ "\n");
				else if (temp.equals("tradesweek"))
					out.write(tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + ","
							+ tempUser.getTradesweek() + ","
							+ tempUser.getName() + "\n");
				else
					out.write(tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + ","
							+ tempUser.getnumLogins() + ","
							+ tempUser.getName() + "\n");
			}
			out.close();
		} catch (Exception f) {// Catch exception if any
			log("Error writing to output file", f);
		}
	}

	private static void getCoords() throws Exception {
		try {
			int lineNum = 0;
			int mins = users.size() / 2;
			mins /= 60;
			int hrs = (int) (mins / 60);
			mins %= 60;
			ListIterator<User> it = users.listIterator();
			while (it.hasNext()) {
				User tempUser = it.next();
				String IP = tempUser.getIpaddr();
				try {
					Thread.currentThread();
					Thread.sleep(DELAY);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
				// System.out.println(IP + " " + tempUser.getIpaddr() + " " +
				// tempUser.getUserid());
				URL url = new URL(URL + IP);
				InputStream response = url.openStream();
				BufferedReader reader = new BufferedReader(
						new InputStreamReader(response));
				int length = users.size();
				for (String s; (s = reader.readLine()) != null;) {
					// while ((s = r.readLine())!=null) {
					lineNum++;
					double complete = (double) lineNum / length;
					int remaining = length - lineNum;
					remaining /= 2;
					mins = remaining / 60;
					mins %= 60;
					hrs = (int) (mins / 60);
					String minutes;
					minutes = String.valueOf(mins);
					DecimalFormat df = new DecimalFormat("#.##");
					complete *= 100;
					if (hrs != 0)
						System.out.print("\rEstimated completion time: " + hrs
								+ " hours and " + minutes + " minutes. "
								+ lineNum + " of " + length + " "
								+ df.format(complete) + "% complete...   ");
					else {
						if (mins != 0)
							System.out.print("\rEstimated completion time: "
									+ minutes + " minutes. " + lineNum + " of "
									+ length + " " + df.format(complete)
									+ "% complete...   ");
						else
							System.out.print("\rEstimated completion time: "
									+ remaining + " seconds. " + lineNum
									+ " of " + length + " "
									+ df.format(complete) + "% complete...   ");
					}
					// System.out.println(s);
					String m = s.replace(',', ':');
					String[] result = m.split(";");
					String lat = "-";
					String lon = "-";
					if (result.length >= 10) {
						lat = result[8];
						lon = result[9];
					}
					tempUser.setIpaddr(result[2]);
					tempUser.setCountry(result[4]);
					tempUser.setCity(result[6]);
					tempUser.setState(result[5]);
					tempUser.setLat(lat);
					tempUser.setLon(lon);
				}
				reader.close();
			}
			System.out.println("\nComplete!");
		} catch (IOException ioe) {
			log("IO Exception", ioe);
		}
	}

}
