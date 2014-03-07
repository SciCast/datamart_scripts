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
import java.util.Date;
import java.util.ListIterator;
import java.util.Properties;

import javax.activation.DataHandler;
import javax.activation.DataSource;
import javax.activation.FileDataSource;
import javax.mail.Authenticator;
import javax.mail.BodyPart;
import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.PasswordAuthentication;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeBodyPart;
import javax.mail.internet.MimeMessage;
import javax.mail.internet.MimeMultipart;

public class pay {

	public static String HOST = "";
	public static String SENDFROM = "";
	public static String USER = "daggre_awards";
	public static String PASS = "";
	public static String PORT = "587";
	public static String CONFIG = "geolocate.cfg";
	public static String NEWWINNERS = "newwinners.csv";
	public static String LOGFILE = "geolocate.log";
	public static String BODYFILE = "bodyfile.txt";
	public static String EMAILLOG = "emails.csv";
	public static String AMAZON = "amazoncodes.csv";
	public static String DAGGREPIC = "daggre.gif";
	public static String AMAZONPIC = "amazon.gif";
	public static int DEBUG = 0;
	public static ArrayList<String[]> WINNERS = new ArrayList<String[]>();
	public static ArrayList<String> AmazonCodes = new ArrayList<String>();
	public static ArrayList<String> logOutput = new ArrayList<String>();

	public static void main(String[] args) {
		if (args.length != 0) {
			if (args[0].length() == 1)
				DEBUG = Integer.parseInt(args[0]);
		}
		File f = new File(CONFIG);
		String body = "";
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
					if (strLine.matches("(?i)^SENDFROM:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							SENDFROM = tempNum;
					} else if (strLine.matches("(?i)^USER:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							USER = tempNum;
					} else if (strLine.matches("(?i)^PORT:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							PORT = tempNum;
					} else if (strLine.matches("(?i)^BODYFILE:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							BODYFILE = tempNum;
					} else if (strLine.matches("(?i)^PASS:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							PASS = tempNum;
					} else if (strLine.matches("(?i)^EMAILLOG:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							EMAILLOG = tempNum;
					} else if (strLine.matches("(?i)^NEWWINNERS:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							NEWWINNERS = tempNum;
					} else if (strLine.matches("(?i)^HOST:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							HOST = tempNum;
					} else if (strLine.matches("(?i)^DAGGREPIC:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							DAGGREPIC = tempNum;
					} else if (strLine.matches("(?i)^AMAZONPIC:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							AMAZONPIC = tempNum;
					} else if (strLine.matches("(?i)^AMAZONCODES:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							AMAZON = tempNum;
					} else if (strLine.matches("(?i)^LOGFILE:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							LOGFILE = tempNum;
					} else if (strLine.matches("^#.*") || strLine.length() == 0)
						continue;
					else {
						System.out.println(strLine);
						log("Config file error; line: " + strLine,
								new Exception());
					}
					br.close();
				}
			} catch (Exception e) {
				log("Problem reading config file", new FileNotFoundException());
			}
		}
		try {
			// Create file
			FileInputStream fstream = new FileInputStream(NEWWINNERS);
			// Get the object of DataInputStream
			DataInputStream in = new DataInputStream(fstream);
			BufferedReader br = new BufferedReader(new InputStreamReader(in));
			String strLine = "";
			// Read File Line By Line
			while ((strLine = br.readLine()) != null) {
				String[] temp = strLine.split(",");
				WINNERS.add(temp);
			}
			// System.out.println(messageText);
			// Close the output stream
			in.close();
			fstream = new FileInputStream(BODYFILE);
			in = new DataInputStream(fstream);
			br = new BufferedReader(new InputStreamReader(in));
			body = "";
			while ((strLine = br.readLine()) != null) {
				body += strLine;
			}
			in.close();
			fstream = new FileInputStream(AMAZON);
			// Get the object of DataInputStream
			in = new DataInputStream(fstream);
			br = new BufferedReader(new InputStreamReader(in));
			strLine = "";
			// Read File Line By Line
			while ((strLine = br.readLine()) != null) {
				if (!strLine.matches("(?i).*USED.*"))
					AmazonCodes.add(strLine);
				else
					continue;
			}
			in.close();

		} catch (Exception e) {// Catch exception if any
			log("File Not Found", e);
		}
		ListIterator<String[]> it = WINNERS.listIterator();
		ListIterator<String> it2 = AmazonCodes.listIterator();
		String[] temp2 = null;
		while (it.hasNext()) {
			String[] temp = it.next();
			String temp1 = it2.next();
			temp2 = temp1.split(",");
			String recipient = "";
			if (DEBUG == 1)
				recipient = temp[3];
			else
				recipient = temp[3] + ".rpost.org";
			String header = body.replaceFirst("<<NAME>>", temp[2]);
			header = header.replaceFirst("<<CODE>>", temp2[0]);
			String logput = temp[4] + "," + temp[0] + "," + temp[2] + ","
					+ recipient + "," + temp[5] + "," + temp2[0] + "\n";
			String[] val = { recipient, header, logput };
			// date, userid, name, email, activity level, Amazon Gift Card
			// electronic code
			/*
			 * String output2 = tempUser.getUserid() + "," + tempUser.getName()
			 * + "," + tempUser.getEmail() + "," + now.getYear() + "-" +
			 * now.getMonthOfYear() + "," + tempUser.getAccumulation() + "\n";
			 */
			it2.set(temp2[0] + ",USED");
			sendEmail(val);
		}
		FileWriter fstream2;
		try {
			fstream2 = new FileWriter(AMAZON);
			BufferedWriter out2 = new BufferedWriter(fstream2);
			ListIterator<String> it1 = AmazonCodes.listIterator();
			while (it1.hasNext())
				out2.write(it1.next() + "\n");
			out2.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	private static void sendEmail(String[] messageInfo) {
		// Get system properties
		Properties props = new Properties();
		props.put("mail.smtp.user", USER);
		props.put("mail.smtp.host", HOST);
		props.put("mail.smtp.port", PORT);
		props.put("mail.smtp.starttls.enable", "true");
		props.put("mail.smtp.auth", "true");
		props.put("mail.smtp.debug", "true");
		props.put("mail.smtp.socketFactory.port", PORT);
		Authenticator auth = new SMTPAuthenticator();
		Session session = Session.getInstance(props, auth);
		props.put("mail.smtp.socketFactory.fallback", "false");
		MimeMultipart multipart = new MimeMultipart("related");
		try {
			FileWriter fstream = new FileWriter(EMAILLOG, true);
			BufferedWriter out = new BufferedWriter(fstream);
			MimeMessage message = new MimeMessage(session);
			message.setFrom(new InternetAddress(SENDFROM));
			message.addRecipient(Message.RecipientType.TO, new InternetAddress(
					messageInfo[0]));
			message.setSubject("DAGGRE compensation notification");
			// Create the body portion (text/html)
			BodyPart messageBodyPart = new MimeBodyPart();
			messageBodyPart.setContent(messageInfo[1], "text/html");
			multipart.addBodyPart(messageBodyPart);

			// Import the daggre picture
			messageBodyPart = new MimeBodyPart();
			DataSource fds1 = new FileDataSource(DAGGREPIC);
			messageBodyPart.setFileName(DAGGREPIC);
			messageBodyPart.setDataHandler(new DataHandler(fds1));
			messageBodyPart.setHeader("Content-ID", "<@dag_image>");

			// add it
			multipart.addBodyPart(messageBodyPart);

			// Import the amazon picture
			messageBodyPart = new MimeBodyPart();
			DataSource fds = new FileDataSource(AMAZONPIC);
			messageBodyPart.setDataHandler(new DataHandler(fds));
			messageBodyPart.setFileName(AMAZONPIC);
			messageBodyPart.setHeader("Content-ID", "<@ama_image>");

			// add it
			multipart.addBodyPart(messageBodyPart);

			// Add the multipart-body to the e-mail
			message.setContent(multipart);
			Transport.send(message);

			out.write(messageInfo[2]);
			out.close();
		} catch (MessagingException mex) {
			mex.printStackTrace();
		}// */
		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	protected static void log(String message, Exception e) {
		try {
			// Create file
			FileWriter fstream = new FileWriter(LOGFILE, true);
			BufferedWriter out = new BufferedWriter(fstream);
			Date current = new Date();
			String now = current.toString();
			if (DEBUG == 1)
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

	private static class SMTPAuthenticator extends javax.mail.Authenticator {
		public PasswordAuthentication getPasswordAuthentication() {
			return new PasswordAuthentication(USER, PASS);
		}
	}
}
