import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Date;
import java.util.Properties;

import javax.activation.DataHandler;
import javax.activation.DataSource;
import javax.activation.FileDataSource;
import javax.mail.Authenticator;
import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.Multipart;
import javax.mail.PasswordAuthentication;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeBodyPart;
import javax.mail.internet.MimeMessage;
import javax.mail.internet.MimeMultipart;

public class getWinners {

	public static String SENDTO = "";
	public static String HOST = "";
	public static String SENDFROM = "";
	public static String USER = "daggre_awards";
	public static String PASS = "";
	public static String PORT = "587";
	public static String USERDB = "users.db";
	public static String PASTDB = "users_prev.csv";
	public static String CONFIG = "geolocate.cfg";
	public static String LOGFILE = "geolocate.log";
	public static String OUTPUT = "winnerLog.db";
	public static String NEWWINNERS = "newwinners.csv";
	public static String TYPE = "";
	public static String eligibleFile = "eligibleList.csv";
	public static int DEBUG = 0;
	public static int THRESH = 8;

	public static void main(String[] args) {
		if (args.length != 0) {
			if (args[0].length() == 1)
				DEBUG = Integer.parseInt(args[0]);
			else
				CONFIG = args[0];
		}
		File f = new File(CONFIG);
		System.out.println(CONFIG);
		System.out.println(f.exists());
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
					if (strLine.matches("(?i)^SENDTO:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							SENDTO = tempNum;
					} else if (strLine.matches("(?i)^SENDFROM:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							SENDFROM = tempNum;
					} else if (strLine.matches("(?i)^LOGFILE:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							LOGFILE = tempNum;
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
					} else if (strLine.matches("(?i)^PASS:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							PASS = tempNum;
					} else if (strLine.matches("(?i)^USERDB:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							USERDB = tempNum;
					} else if (strLine.matches("(?i)^NEWWINNERS:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							NEWWINNERS = tempNum;
					} else if (strLine.matches("(?i)^WINNERLOG:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							OUTPUT = tempNum;
					} else if (strLine.matches("(?i)^PASTDB:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							PASTDB = tempNum;
					} else if (strLine.matches("(?i)^HOST:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							HOST = tempNum;
					} else if (strLine.matches("(?i)^ELIGIBLE:.+")) {
						String[] temp = strLine.split(":");
						String tempNum = temp[1].trim();
						if (tempNum.length() != 0)
							eligibleFile = tempNum;
					} else if (strLine.matches("^#.*") || strLine.length() == 0)
						continue;
					else {
						System.out.println(strLine);
						// log("Config file error; line: " + strLine,
						// new Exception());
					}
				}
				br.close();
			} catch (Exception e) {
				log("Problem reading config file", new FileNotFoundException());
			}
			Userdb database = new Userdb();
			String messageText = "";
			try {
				messageText = database.getEligible();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			sendEmail(messageText);
		}
	}

	private static void sendEmail(String messageText) {

		Properties props = new Properties();
		props.put("mail.smtp.user", USER);
		props.put("mail.smtp.host", HOST);
		props.put("mail.smtp.port", PORT);
		props.put("mail.smtp.starttls.enable", "true");
		props.put("mail.smtp.auth", "true");
		props.put("mail.smtp.debug", "true");
		props.put("mail.smtp.socketFactory.port", PORT);
		// props.put("mail.smtp.socketFactory.class",
		// "javax.net.ssl.SSLSocketFactory");
		props.put("mail.smtp.socketFactory.fallback", "false");

		// SecurityManager security = System.getSecurityManager();

		try {
			Authenticator auth = new SMTPAuthenticator();
			Session session = Session.getInstance(props, auth);
			// session.setDebug(true);

			// Define message
			MimeMessage message = new MimeMessage(session);
			message.setFrom(new InternetAddress(SENDFROM));
			if (DEBUG == 2)
				message.addRecipient(Message.RecipientType.TO,
						new InternetAddress(""));
			else {
				message.addRecipient(Message.RecipientType.TO,
						new InternetAddress(SENDTO));
				// message.addRecipient(Message.RecipientType.CC, new
				// InternetAddress(""));
			}
			message.setSubject("DAGGRE compensation notification");

			// create the message part
			MimeBodyPart messageBodyPart = new MimeBodyPart();

			// fill message
			messageBodyPart.setText(messageText);

			Multipart multipart = new MimeMultipart();
			multipart.addBodyPart(messageBodyPart);

			// Part two is attachment
			messageBodyPart = new MimeBodyPart();
			DataSource source = new FileDataSource(NEWWINNERS);
			messageBodyPart.setDataHandler(new DataHandler(source));
			messageBodyPart.setFileName(NEWWINNERS);
			multipart.addBodyPart(messageBodyPart);

			// Part three is also an attachment
			messageBodyPart = new MimeBodyPart();
			source = new FileDataSource(OUTPUT);
			messageBodyPart.setDataHandler(new DataHandler(source));
			messageBodyPart.setFileName("winnerlog.csv");
			multipart.addBodyPart(messageBodyPart);

			// Part four is also an attachment
			messageBodyPart = new MimeBodyPart();
			source = new FileDataSource(eligibleFile);
			messageBodyPart.setDataHandler(new DataHandler(source));
			messageBodyPart.setFileName(eligibleFile);
			multipart.addBodyPart(messageBodyPart);

			// Put parts in message
			message.setContent(multipart);

			// Send the message
			Transport.send(message);

		} catch (MessagingException mex) {
			mex.printStackTrace();
		}// */

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

	protected static class SMTPAuthenticator extends javax.mail.Authenticator {
		public PasswordAuthentication getPasswordAuthentication() {
			return new PasswordAuthentication(USER, PASS);
		}
	}
}
