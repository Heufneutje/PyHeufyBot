<?php header('Content-type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link rel="stylesheet" type="text/css" href="loglook.css">
<script src="eventsscript.js"></script>
<title>
<?php
//First and foremost, some input validation
$network = (isset($_GET['network']) ? htmlspecialchars($_GET['network']) : FALSE);
$channel = (isset($_GET['channel']) ? htmlspecialchars($_GET['channel']) : FALSE);
$date = (preg_match('/\A\d{4}-\d{2}-\d{2}\z/', $_GET['date']) === 1 ? htmlspecialchars($_GET['date']) : FALSE);
$hideEvents = FALSE;
if (isset($_GET['hideevents']) and $_GET['hideevents'] === 'true') {
	$hideEvents = TRUE;
}

if ($network !== FALSE and $channel !== FALSE and $date !== FALSE) {
	echo 'Log for #'.$channel.' on '.$network.' from '.$date;
	if ($hideEvents) echo ' with events hidden';
}
else echo 'Log Prettifier';
?>
</title>
</head>
<body>
<?php
if ($network === FALSE) echo 'No network name provided!';
elseif ($channel === FALSE) echo 'No channel name provided!';
elseif($date === FALSE) echo 'No date provided!';
else {
	$filename = '/home/stefan/logs/'.$network.'/#'.$channel.'/'.$date.'.log';
	$lines = file($filename, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES); 
	unset($filename);
	if ($lines === FALSE) echo 'Error while trying to open log file.';
	elseif (count($lines) === 0) echo 'No lines found in the log file';
	else {
		$eventLinkUrl = $_SERVER['REQUEST_URI'];
		//If there's already a hideevents setting, replace that
		if (strpos($eventLinkUrl, 'hideevents') !== FALSE) {
			$eventLinkUrl = preg_replace('/hideevents=[^&\z]+/', 'hideevents='.($hideEvents?'false':'true'), $eventLinkUrl);
		}
		//otherwise, add it on
		else $eventLinkUrl .= '&hideevents='.($hideEvents?'false':'true');
		echo '<p><span><a href="'.$eventLinkUrl.'">'.($hideEvents?'Show':'Hide').' events</a></span></p>'."\r\n";
		
		echo '<table class="log" id="log"><tr class="message"> <th class="time">TIME</th> <th class="user">NICK</th> <th class="text">MESSAGE</th></tr>'."\r\n";
		//Get the length of the first section of the first line, which is assumed to be the timestamp
		$timestampLength = strlen(explode(' ', $lines[0], 2)[0]);
		$suffixCharactersToRemove = array(')', '.');
		$linecount = count($lines);
		
		//Reverse the array so we can pop lines off the end, which is faster than getting them from the start
		$lines = array_reverse($lines);
		for ($i = 0; $i < $linecount; $i++) {
			$line = htmlspecialchars(array_pop($lines));
			if (strlen($line) > 0) {
				$lineSections = explode(' ', $line);
				$messageType = 'message';
				$nickType = 'user';
				//if there isn't both a < and a >, it's not a nick but an action or join/quit message. Change how that looks
				if (strpos($lineSections[1], '&lt;') === FALSE or strpos($lineSections[1], '&gt;') === FALSE) {
					if ($lineSections[1] === '*') $messageType = 'action';
					else $messageType = 'other';
					$nickType = 'spacer';
				}
				//If we should hide events, just skip the echo-ing when it's a join or quit
				if ($hideEvents and $messageType === 'other') {
					continue;
				}
				$message = substr($line, $timestampLength + strlen($lineSections[1])+2);
				//Turn URLs into hyperlinks
				if (strpos($message, 'http') !== FALSE or strpos($message, 'www') !== FALSE) {
					preg_match_all("/(https?:\/\/\S+|www\.\S+\.\S+)/", $message, $regexResults);
					foreach ($regexResults[0] as $urlText) {
						//Remove some trailing characters that can mess up the url, like periods or parentheses
						while (in_array(mb_substr($urlText, -1, 1), $suffixCharactersToRemove)) {
							$urlText = mb_substr($urlText, 0, -1);
						}
						
						//The display text can be different from the actual link it should be
						$url = $urlText;	
						//Make sure the url actually starts with 'http' if there's no protocol specified
						if (strpos($url, 'http://') !== 0 and strpos($url, 'https://') !== 0 and strpos($url, 'ftp://') !== 0) {
							$url = 'http://'.$url;
						}
						
						//Finally, actually change the text to a hyperlink
						$message = str_replace($urlText, '<a href="'.$url.'" target="_blank">'.$urlText.'</a>', $message);
					}
				}
				
				echo '<tr class="'.$messageType.'">';
				echo '<td class="time"><a id="line'.$i.'" href="#line'.$i.'">'.$lineSections[0].'</a></td>';
				echo '<td class="'.$nickType.'">'.$lineSections[1].'</td> ';
				echo '<td class="text">'.$message.'</td>';
				echo "</tr>\r\n";
			}
		}
		echo "</table>\r\n";
	}
}
?>
</body>
</html>
