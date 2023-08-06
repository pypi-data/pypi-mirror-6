<!-- -*- coding: utf-8 -*-
-- :Progetto:  SoL
-- :Creato:    gio 06 nov 2008 17:24:19 CET
-- :Autore:    Lele Gaifax <lele@metapensiero.it>
-- :Licenza:   GNU General Public License version 3 or later
-- -->

<html>
  <head>
    <title>${_('SoL Clock')}</title>

    % for group, sheets in stylesheets:
    <!-- ${group} -->
      % for sheet in sheets:
    <link rel="stylesheet" type="text/css" href="${sheet}"></link>
      % endfor

    % endfor
    <!--[if IE]><script type="text/javascript" src="/static/clock/excanvas.js"></script><![endif]-->

    % for group, scripts in javascripts:
    <!-- ${group} -->
      % for script in scripts:
    <script type="text/javascript" src="${script}"></script>
      % endfor

    % endfor
    <!-- Sounds initialization -->
    <script type="text/javascript">
      soundManager.setup({
        url: '/static/clock/', // directory where SM2 .SWFs live
        debugMode: false,
        onready: function() {
          soundManager.createSound('tic','/static/sounds/tic.mp3');
          soundManager.createSound('tac','/static/sounds/tac.mp3');
          soundManager.createSound('start','/static/sounds/start.mp3');
          soundManager.createSound('prealarm','/static/sounds/prealarm.mp3');
          soundManager.createSound('stop','/static/sounds/stop.mp3');
        }
      });
    </script>
  </head>

  <body>
    <div>
      <!-- soundManager appends "hidden" Flash to the first DIV on the page. -->
    </div>

    <h2 class="centered">${_('Playing turn %d')%currentturn}</h2>

    <table class="centered">
      <tbody>
        <tr>
          <td rowspan="2">
            <canvas id="c1" class="CoolAlarmClock:swissRail::noSeconds::::${duration}:${prealarm}"></canvas>
          </td>
          <td class="centered">${_('%d minutes, %d minutes of prealarm')%(duration,prealarm)}</td>
        </tr>
        <tr>
          <td width="50%" id="c1-time-left" class="timeleft centered"></td>
        </tr>
      </tbody>
    </table>
    <div class="centered hint">
      <button type="button"
              onclick="document.getElementById('c1').startCountdown();">
        ${_('(Re)start the countdown immediately')}
      </button>
      ${_('or')}
      <button type="button"
              onclick="document.getElementById('c1').startDelayedCountdown(15000);">
        ${_('do it in 15 seconds')}
      </button>
      &nbsp;
      <button type="button" onclick="window.close();">
        ${_('Close the window to stop')}
      </button>
    </div>
  </body>
</html>
