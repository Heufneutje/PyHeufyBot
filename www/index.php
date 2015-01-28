<?php header('Content-type: text/html; charset=utf-8'); ?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link rel="stylesheet" type="text/css" href="loglook.css">
<script src="eventsscript.js"></script>
<title>
<?php
$starttime = microtime(TRUE);
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

	if ($lines === FALSE) echo 'Error while trying to open log file.';
	elseif (count($lines) === 0) echo 'No lines found in the log file';
	else {
		unset($filename);
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
		//Character constants used for adding colour to IRC messages
		$COLOUR_CHAR = '';
		$CANCEL_CHAR = '';
		$BOLD_CHAR = '';
		$openStyles = array('background' => '', 'foreground' => '', 'bold' => FALSE);
		//A function that'll get called for each message with $COLOUR_CHAR or $BOLD_CHAR in it, that styles the message accordingly
		function handleStyleCharacters($matches) {
			global $COLOUR_CHAR, $CANCEL_CHAR, $BOLD_CHAR, $openStyles;
			$replacementText = '';
			//If we're already doing something, anything, stop doing that.
			if ($openStyles['background'] !== '' or $openStyles['foreground'] !== '' or $openStyles['bold'] === TRUE) {
				$replacementText .= '</span>';
			}
			//Bold text. If we're already doing bold, stop it. If we're not, start
			if ($matches[0] === $BOLD_CHAR) {
				$openStyles['bold'] = !$openStyles['bold'];
			}
			//Colour char. If it's only that, clear colours. If it's followed by just one number, it's just foreground colour. Two numbers is fore- and background
			elseif (strpos($matches[0], $COLOUR_CHAR) !== FALSE) {
				//A single colour character. Clear all colours
				if ($matches[0] === $COLOUR_CHAR) {
					$openStyles['background'] = '';
					$openStyles['foreground'] = '';
				}
				//We've got at least a foreground colour
				else {
					$openStyles['foreground'] = $matches[2];
					//There's a background colour too (which includes the comma)
					if (isset($matches[3])) {
						$openStyles['background'] = ltrim($matches[3], ',');
					}
				}
			}
			//We either reached a Cancel char, or the end of the sentence. Cleanup time!
			else {
				$openStyles['background'] = '';
				$openStyles['foreground'] = '';
				$openStyles['bold'] = FALSE;
			}
			
			//Now that all the parsing is done, construct the new <span>, if necessary
			if ($openStyles['background'] !== '' or $openStyles['foreground'] !== '' or $openStyles['bold'] === TRUE) {
				$replacementText .= '<span class="';
				if ($openStyles['background'] !== '') {
					$replacementText .= 'bg'.$openStyles['background'].' ';
				}
				if ($openStyles['foreground'] !== '') {
					$replacementText .= 'fg'.$openStyles['foreground'].' ';
				}
				if ($openStyles['bold'] === TRUE) {
					$replacementText .= 'bold';
				}
				$replacementText = rtrim($replacementText).'">';
			}
			return $replacementText;
		}

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
				
				//Parse colour and bold codes, if necessary
				if (strpos($message, $COLOUR_CHAR) !== FALSE or strpos($message, $BOLD_CHAR) !== FALSE) {
					$message = preg_replace_callback("/($COLOUR_CHAR(\d{1,2})(,\d{1,2})?|${COLOUR_CHAR}(?=[^\d])|$BOLD_CHAR|$CANCEL_CHAR|$)/", 'handleStyleCharacters', $message);
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
echo '<br><br>Execution took '.(microtime(TRUE) - $starttime).' ms';
?>
</body>
</html>
