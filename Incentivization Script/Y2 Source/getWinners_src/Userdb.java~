import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.ListIterator;
import java.util.Random;

import org.joda.time.LocalDate;

public class Userdb {

	private int MAX = 0;
	private String runningOutput = "";
	private ArrayList<User> users = new ArrayList<User>();
	private ArrayList<User> eligible = new ArrayList<User>();
	private ArrayList<User> winners = new ArrayList<User>();
	private ArrayList<User> eligible_last = new ArrayList<User>();
	private ArrayList<User> wonLast = new ArrayList<User>();
	private ArrayList<String[]> prevUsers = new ArrayList<String[]>();

	public Userdb() {
		FileInputStream fstream;
		try {
			fstream = new FileInputStream(getWinners.USERDB);
			// Get the object of DataInputStream
			DataInputStream in = new DataInputStream(fstream);
			BufferedReader br = new BufferedReader(new InputStreamReader(in));
			String line = "";
			line = br.readLine();
			String[] s = line.split(",");
			getWinners.THRESH = Integer.parseInt(s[0]);
			getWinners.TYPE = s[1];
			while ((line = br.readLine()) != null) {
				String[] temp = line.split(",");
				if (temp[0] == "")
					break;
				int id = Integer.parseInt(temp[0]);
				int Accumulation = Integer.parseInt(temp[3]);
				String email = temp[2];
				String username = temp[1];
				String name = temp[4];
				User tempUser = new User(id, username, email, Accumulation,
						name, getWinners.TYPE);
				users.add(tempUser);
			}
			fstream.close();
			File f = new File(getWinners.PASTDB);
			if (f.exists()) {
				fstream = new FileInputStream(getWinners.PASTDB);
				in = new DataInputStream(fstream);
				br = new BufferedReader(new InputStreamReader(in));
				line = br.readLine();
				if (line != null) {
					String type = line;
					line = br.readLine();
					String[] temp = line.split(",");
					prevUsers.add(temp);
					while ((line = br.readLine()) != null) {
						temp = line.split(",");
						if (temp.length == 1)
							break;
						User tempUser = new User();
						String[] prevValues = Arrays.copyOfRange(temp, 4,
								temp.length);
						String[] prevUserValue = new String[prevValues.length + 1];
						int sum = 0;
						for (int i = 0; i < prevValues.length; i++) {
							prevUserValue[i] = prevValues[i];
							sum += Integer.parseInt(prevUserValue[i]);
						}
						sum += Integer.parseInt(temp[temp.length - 1]);
						prevUserValue[prevValues.length] = "" + temp[0];
						prevUsers.add(prevUserValue);
						tempUser.setUserid(Integer.parseInt(temp[0]));
						if (users.contains(tempUser)) {
							User temp2 = users.get(users.indexOf(tempUser));
							// temp2.addAccumulation(type,Integer.parseInt(temp[temp.length
							// - 1]));
							temp2.addAccumulation(type, sum);
							users.set(users.indexOf(tempUser), temp2);
						} else {
							tempUser.setUsername(temp[1]);
							tempUser.setEmail(temp[2]);
							if (type.equals("trades90"))
								tempUser.setTrades90(Integer
										.parseInt(temp[temp.length - 1]));
							else if (type.equals("trades30"))
								tempUser.setTrades30(Integer
										.parseInt(temp[temp.length - 1]));
							else if (type.equals("tradesweek"))
								tempUser.setTradesweek(Integer
										.parseInt(temp[temp.length - 1]));
							else
								tempUser.setNumLogins(Integer
										.parseInt(temp[temp.length - 1]));
							tempUser.setName(temp[3]);
							users.add(tempUser);
						}
						if (Integer.parseInt(temp[temp.length - 1]) >= getWinners.THRESH) {
							eligible_last
									.add(users.get(users.indexOf(tempUser)));
							runningOutput += users.get(users.indexOf(tempUser))
									.getUsername() + ";Eligible last\n";
						}
					}
				}
			}
			fstream.close();
			fstream = new FileInputStream(getWinners.OUTPUT);
			in = new DataInputStream(fstream);
			br = new BufferedReader(new InputStreamReader(in));
			LocalDate now = new LocalDate();
			int year = now.getYear();
			int month = now.getMonthOfYear();
			month -= 1;
			while ((line = br.readLine()) != null) {
				String[] temp = line.split(",");
				if (temp[3].equalsIgnoreCase(year + "-" + month)) {
					User tempUser = new User();
					// System.out.println(temp[0]);
					tempUser.setUserid(Integer.parseInt(temp[0]));
					wonLast.add(users.get(users.indexOf(tempUser)));
					runningOutput += users.get(users.indexOf(tempUser))
							.getUsername() + ";Won last\n";
				}
			}
			in.close();
			br.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	protected String getEligible() throws IOException {

		ListIterator<User> it = users.listIterator();
		// System.out.println("total user size: "+activeUsers.size());
		while (it.hasNext()) {
			User tempUser = it.next();
			tempUser.addAccumulation(getWinners.TYPE);
			if (tempUser.getAccumulation() >= getWinners.THRESH)
				eligible.add(tempUser);
		}
		if (eligible.size() < 60) {
			eligible.clear();
			getWinners.THRESH /= 2;
			if (getWinners.THRESH == 1) {
				getWinners.log(
						"No users participated more than once, exit code 999",
						new InadequateUsersException());
				System.exit(999);
			}
			return getEligible();
		} else {
			/*
			 * done: get active users where !mercyhurst && trades >= THRESH &&
			 * !prevWinners || get active users where !mercyhurst && trades >=
			 * THRESH || get active users where !mercyhurst && 1 < trades >=
			 * THRESH-x or die; todo: Assumed we have an eligible size of >= 60
			 * randomize with bias on users in eligible write 60 to log, send
			 * e-mail
			 */
			it = eligible.listIterator();
			ArrayList<Integer> edits = new ArrayList<Integer>();
			while (it.hasNext()) {
				User tempUser = it.next();
				edits.add(tempUser.getAccumulation());
			}
			Collections.sort(edits);
			int percentLocation = edits.size();
			percentLocation *= .9;
			MAX = Math.max(edits.get(percentLocation), getWinners.THRESH);
			it = eligible.listIterator();
			ArrayList<User> hat = new ArrayList<User>();
			while (it.hasNext()) {
				User tempUser = it.next();
				int min = Math.min(MAX, tempUser.getAccumulation());
				runningOutput += "ID;" + tempUser.getUsername() + ";" + min
						+ "\n";
				for (int i = 0; i < min; i++)
					hat.add(tempUser);
			}
			Random random = new Random(System.identityHashCode(users));
			Collections.shuffle(hat, random);
			it = hat.listIterator();
			while (it.hasNext()) {
				User tempUser = it.next();
				runningOutput += tempUser + "\n";
				if (winners.size() == 60)
					break;
				if (!winners.contains(tempUser))
					winners.add(tempUser);
				// else
				// winners.add(tempUser);
			}
			// Now we have our list of winners, we check for two-time winners
			ArrayList<User> twoTimeWinners = new ArrayList<User>();
			ArrayList<User> twoTimeLosers = new ArrayList<User>();
			ListIterator<User> temp = winners.listIterator();
			while (temp.hasNext()) {
				User tempUser = temp.next();
				if (wonLast.contains(tempUser))
					twoTimeWinners.add(tempUser);
			}
			temp = eligible_last.listIterator();
			while (temp.hasNext()) {
				User tempUser = temp.next();
				if (!winners.contains(tempUser))
					twoTimeLosers.add(tempUser);
			}
			if (twoTimeLosers.size() == 0)
				return saveWinners();
			else {
				FileWriter fstream = new FileWriter("swaps.csv", true);
				BufferedWriter out = new BufferedWriter(fstream);
				if (twoTimeWinners.size() == twoTimeLosers.size()) {
					temp = winners.listIterator();
					Collections.shuffle(twoTimeLosers, random);
					ListIterator<User> swapUser = twoTimeLosers.listIterator();
					while (temp.hasNext()) {
						User tempUser = temp.next();
						if (twoTimeWinners.contains(tempUser)) {
							if (swapUser.hasNext()) {
								User userSwap = swapUser.next();
								temp.set(userSwap);
								runningOutput += "==;" + tempUser + ";"
										+ userSwap + "\n";
							} else
								break;
						} else
							continue;
					}
				} else if (twoTimeWinners.size() > twoTimeLosers.size()) {
					Collections.shuffle(twoTimeLosers, random);
					Collections.shuffle(twoTimeWinners, random);
					ListIterator<User> losers = twoTimeLosers.listIterator();
					ListIterator<User> winner = twoTimeWinners.listIterator();
					while (losers.hasNext()) {
						temp = winners.listIterator(0);
						User tempUser = losers.next();
						User removeUser = winner.next();
						while (temp.hasNext()) {
							User winnerToRemove = temp.next();
							if (winnerToRemove.equals(removeUser)) {
								temp.set(tempUser);
								runningOutput += ">;" + tempUser + ";"
										+ winnerToRemove + "\n";
							}
						}
						losers.remove();
					}

				} else { // twoTimeWinners.size() < twoTimeLosers.size()
					temp = winners.listIterator();
					Collections.shuffle(twoTimeLosers, random);
					ListIterator<User> losers = twoTimeLosers.listIterator();
					ListIterator<User> winner = twoTimeWinners.listIterator();
					while (winner.hasNext()) {
						User userToRemove = winner.next();
						User userToAdd = losers.next();
						while (temp.hasNext()) {
							User winnerToRemove = temp.next();
							if (winnerToRemove.equals(userToRemove)) {
								temp.set(userToAdd);
								runningOutput += "<;" + winnerToRemove + ";"
										+ userToAdd + "\n";
							}
						}
						losers.remove();
					}
				}
				if (twoTimeLosers.size() != 0) {
					Collections.shuffle(twoTimeLosers, random);
					Collections.shuffle(winners, random);
					ListIterator<User> losers = twoTimeLosers.listIterator();
					temp = winners.listIterator();
					while (temp.hasNext()) {
						runningOutput += "End;";
						runningOutput += temp.next();
						User tempUser = losers.next();
						runningOutput += ";" + tempUser + "\n";
						temp.set(tempUser);

					}

				}
				out.write(runningOutput);
				out.close();
				fstream.close();
				return saveWinners();
			}
		}
	}

	private String saveWinners() {
		if (winners.size() != 60) {
			System.out.println(winners.size());
			System.exit(1);
		}
		try {
			// Create file
			FileWriter fstream = new FileWriter(getWinners.OUTPUT, true);
			BufferedWriter out = new BufferedWriter(fstream);
			FileWriter fstream2 = new FileWriter(getWinners.NEWWINNERS);
			BufferedWriter out2 = new BufferedWriter(fstream2);
			FileWriter fstream3 = new FileWriter(getWinners.eligibleFile, true);
			BufferedWriter out3 = new BufferedWriter(fstream3);
			ListIterator<User> it = eligible.listIterator();
			LocalDate now = new LocalDate();
			while (it.hasNext()) {
				User tempUser = it.next();
				String output = now.getYear() + "-" + now.getMonthOfYear()
						+ "," + tempUser.getUsername() + ","
						+ tempUser.getAccumulation() + ","
						+ Math.min(MAX, tempUser.getAccumulation()) + "\n";
				out3.write(output);
			}
			out3.close();
			Collections.sort(winners);
			it = winners.listIterator();
			String messageText = "Hello!\nThe following people have been randomly selected "
					+ "to win a compensation award. Please review this list, and download"
					+ " the attachment link below to run the payment script if it is acceptable:\nThe threshold for user participation was "
					+ getWinners.THRESH + " as " + getWinners.TYPE + "\n";
			while (it.hasNext()) {
				User tempUser = it.next();
				String output = tempUser.getUserid() + ","
						+ tempUser.getUsername() + "," + tempUser.getEmail()
						+ "," + now.getYear() + "-" + now.getMonthOfYear()
						+ "," + tempUser.getAccumulation() + ","
						+ tempUser.getName() + "\n";
				messageText += "\n" + tempUser.getUsername()
						+ " with an activity of " + tempUser.getAccumulation()
						+ " in the last month!";
				String output2 = tempUser.getUserid() + ","
						+ tempUser.getUsername() + "," + tempUser.getName()
						+ "," + tempUser.getEmail() + "," + now.getYear() + "-"
						+ now.getMonthOfYear() + ","
						+ tempUser.getAccumulation() + "\n";
				out.write(output);
				out2.write(output2);
				if (users.contains(tempUser)) {
					User temp2 = users.get(users.indexOf(tempUser));
					temp2.resetAccumulation();
				}
			}
			// System.out.println(messageText);
			// Close the output stream
			out.close();
			out2.close();
			out3.close();
			fstream = new FileWriter(getWinners.PASTDB);
			out = new BufferedWriter(fstream);
			if (!prevUsers.isEmpty()) {
				ListIterator<String[]> past = prevUsers.listIterator();
				String output = "";
				out.write(getWinners.TYPE + "\n");
				String[] temp = past.next();
				for (String x : temp) {
					output += x + ",";
				}
				output += now.getYear() + "-" + now.getMonthOfYear() + "\n";
				out.write(output);
				it = users.listIterator();
				while (past.hasNext()) {
					output = "";
					temp = past.next();
					String[] outputArray = Arrays.copyOfRange(temp, 0,
							temp.length - 1);
					User tempUser = new User();
					int var = Integer.parseInt(temp[temp.length - 1]);
					tempUser.setUserid(var);
					if (users.contains(tempUser)) {
						User temp2 = users.get(users.indexOf(tempUser));
						if (winners.contains(tempUser)) {
							output += temp2.getUserid() + ","
									+ temp2.getUsername() + ","
									+ temp2.getEmail() + "," + temp2.getName()
									+ ",";
							for (String x : outputArray) {
								output += x + ",";
							}
							output += 0 + "\n";
						} else {
							output += temp2.getUserid() + ","
									+ temp2.getUsername() + ","
									+ temp2.getEmail() + "," + temp2.getName()
									+ ",";
							for (String x : outputArray) {
								output += x + ",";
							}
							output += temp2.getAccumulation() + "\n";
						}
						users.remove(temp2);
						past.remove();
						out.write(output);
					} else
						continue;
				}
			} else {
				String output = "";
				out.write(getWinners.TYPE + "\n");
				output = "ID,username,email,name," + now.getYear() + "-"
						+ now.getMonthOfYear() + "\n";
				out.write(output);
				it = users.listIterator();
				while (it.hasNext()) {
					output = "";
					User temp = it.next();
					output += temp.getUserid() + "," + temp.getUsername() + ","
							+ temp.getEmail() + "," + temp.getName() + ",";
					output += temp.getAccumulation() + "\n";
					out.write(output);
				}
			}
			it = users.listIterator();
			String[] numPrev = prevUsers.get(0);
			int count = numPrev.length - 4;
			String output = "";
			while (it.hasNext()) {
				User tempUser = it.next();
				if (getWinners.TYPE.equals("trades90")) {
					output = tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + "," + tempUser.getName()
							+ ",";
					for (int i = 0; i < count; i++)
						output += "0,";
					output += tempUser.getTrades90() + "\n";
				} else if (getWinners.TYPE.equals("trades30")) {
					output = tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + "," + tempUser.getName()
							+ ",";
					for (int i = 0; i < count; i++)
						output += "0,";
					output += tempUser.getTrades30() + "\n";
				} else if (getWinners.TYPE.equals("tradesweek")) {
					output = tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + "," + tempUser.getName()
							+ ",";
					for (int i = 0; i < count; i++)
						output += "0,";
					output += tempUser.getTradesweek() + "\n";
				} else {
					output = tempUser.getUserid() + ","
							+ tempUser.getUsername() + ","
							+ tempUser.getEmail() + "," + tempUser.getName()
							+ ",";
					for (int i = 0; i < count; i++)
						output += "0,";
					output += tempUser.getNumLogins() + "\n";
				}
				out.write(output);
			}
			messageText += "\n\nAttached is the newwinners.db file used with the compensation script. You may run this when ready.";
			out.close();
			return messageText;
		} catch (Exception f) {// Catch exception if any
			System.err.println("Error: " + f.getMessage());
			f.printStackTrace();
		}
		return null;
	}

}
