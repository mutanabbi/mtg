<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:local="http://localhost/local"
  >

<xsl:template match="card">
  <xsl:param name="local:set"/>
  <xsl:param name="local:is-active-player" />
  <xsl:variable name="local:class">
    <xsl:choose>
      <xsl:when test="$local:is-active-player and position() = 1">
        <xsl:text>crdbx-act</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>crdbx</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <div class="{$local:class}">
    <!-- DEBUG <xsl:value-of select="position()" /> -->
    <!-- Для некоторых карт-перевертышей из Иннистрад, к номеру перед jpg надо добавлять a или b.
    Сейчас я разрулил это с помощью onerror, но по-хорошему хотелось бы карты перевертыши смотреть
    с обоих сторон. Надо обмозговать, как это реализовать.
    -->
    <img width="100" height="143" class="dv_show_card" alt="Тут будет имя {./@id}" src="http://magiccards.info/scans/en/{$local:set}/{./@id}.jpg" onerror="this.onerror=null;this.src='http://magiccards.info/scans/en/{$local:set}/{./@id}a.jpg';"/>
  </div>
</xsl:template>


<xsl:template match="/">

<html xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" >
<head>
  <title>MTG Draft Viewer</title>
  <link rel="stylesheet" type="text/css" href="draft.css" media="all" />
  <script src="draft.js" />
</head>
<body>

<!-- Формируем шапку с элементами управления -->
<div style="display: block">
  <div class="cntrl-head">
    <img class="line-dlmtr" src="http://mymagic.ru/assets/images/site_tools/line.gif" />
    <div class="cntrl-storage">
      <div style="text-align: center; margin: 20px 0px 0px; display: none;" id="dv_text_title">Вы смотрите запись всех пиков драфта. Чтобы посмотреть процесс драфта, нажмите <a class="dv_image_link" href="javascript:void(0);" style="display: none;">сюда &gt;&gt;</a></div>
      <div style="display: block;" id="dv_image_title">

        <select class="select-vgt" id="dv_player">
          <xsl:for-each select="game/players/player">
            <option value="{position()}"> <xsl:text>Игрок: </xsl:text> <xsl:value-of select="."/> </option>
          </xsl:for-each>
        </select>

        <select class="select-vgt" id="dv_pack">
          <xsl:for-each select="game/boosters/booster">
            <option value="{position()}">
              <xsl:text>Бустер </xsl:text> <xsl:value-of select="position()"/> <xsl:text>: </xsl:text> <xsl:value-of select="."/> </option>
          </xsl:for-each>
        </select>
        <br/>

        <select class="select-vgt" id="dv_pick">
          <xsl:for-each select="game/draft/deck[1]/circle[1]/card">
            <option value="{position()}">
              <xsl:text>Пик </xsl:text> <xsl:value-of select="position()"/></option>
          </xsl:for-each>
        </select>

        <button id="lngSwitcher" type="button" class="select-vgt" onclick="switchLng()">en</button>

        <input type="hidden" value="1" id="dv_pick_n" />
        <input type="checkbox" checked="" id="dv_show_checkbox" class="select-vgt" />
        <label for="dv_show_checkbox" class="select-vgt">показывать выбор игрока</label>
        <div class="blank-dlmtr"></div>

        <div class="prev-vgt">
          <a id="dv_prev_pick_link" href="javascript:void(0);">&lt;&lt; предыдущий пик</a>
        </div>

        <div class="next-vgt">
          <a id="dv_next_pick_link" href="javascript:void(0);" >следующий пик &gt;&gt;</a>
        </div>
      </div>
    </div>

    <div class="players-tbl">
      <div>
        <xsl:for-each select="game/players/player">
          <!-- Тут непонятно. Надо разбираться с правильным порядком-->
          <div class="player-name"><xsl:value-of select="."/></div>
        </xsl:for-each>
        <div class="grey-dlmtr">&#160;</div>
      </div>
    </div>
    <img class="line-dlmtr" src="http://mymagic.ru/assets/images/site_tools/line.gif" />
 </div>

  <!-- Формируем все колоды во время всех пиков по каждому кругу драфта для каждого игрока (для быстрого отображения без релоада впоследствии)-->
  <div id="dv_image_draft" style="display: none">
    <div class="card-storage">

    <!-- Формируем индивидуальные контейнеры для каждого игрока -->
    <xsl:for-each select="/game/players/player">
        <xsl:variable name="local:num" select="count(/game/players/player)" />
        <xsl:variable name="local:cur-player-pos" select="position()" />
        <xsl:variable name="local:cur-player" select="./@id" />
        <div class="dv_image_player{position()}">

        <!-- Формируем контейнеры для каждого круга (для всех пиков в рамках одного бустера). В норме N кругов = N игроков (по бустеру на игрока) -->
        <xsl:for-each select="/game/boosters/booster">
            <xsl:variable name="local:booster" select="./@id" />
            <xsl:variable name="local:set" select="./@set" />
            <xsl:variable name="local:booster-pos" select="position()" />
            <xsl:variable name="local:circle" select="/game/draft/deck[@player=$local:cur-player]/circle[@booster=$local:booster]" />
            <div class="dv_image_pack{position()}">

              <xsl:for-each select="$local:circle/card">
                <xsl:variable name="local:pick-pos" select="position()" />

                <!-- Нижележащий DIV необходимо сгенерировать для каждого пика в игре -->
                <div class="dv_image_pick{$local:pick-pos}">
                  <div class="crdbx">
                    <img width="100" height="143" alt="" src="http://mymagic.ru/assets/images/site_tools/dv_null.jpg" />
                  </div>

                  <!--
                  Еще раз пробегаем по списку игроков, чтобы в правильном порядке расчитать карты из соответствующего пика
                  (порядок объявления игроков в XML определяет их расположение за драфтовым столом - кто по какую руку)
                  -->
                  <xsl:for-each select="/game/players/player">
                    <xsl:variable name="local:player" select="./@id" />
                    <xsl:variable name="local:player-pos" select="position()" />
                    <!--
                    Определяемся с направлением драфта
                    1: По часовой стрелке; -1: против часовой стрелки
                    по дефолтку, первый круг: по часовой стрелке; второй: против; третий: снова по часовой
                    иногда случаются организационные ошибки, так что этот дефолтный порядок можно переопределить,
                    используя атрибут motion ('cw': по часовой стрелке; 'acw': против часовой стрелки)
                    -->
                    <xsl:variable name="local:orientation" select="($local:circle[@motion] = 'cw') + ($local:circle[@motion] = 'acw') + (not(local:circle[@motion]) * (1 - 2 * (($local:booster-pos - 1) mod 2)))" />

                    <xsl:if test="not($local:orientation) or not($local:orientation = 1 or $local:orientation = -1)">
                      <xsl:message terminate="yes">Can't detect draft motion</xsl:message>
                    </xsl:if>
                    <!--
                    <div style="clear: both">
                      <xsl:value-of select="$local:player-pos" />
                      <xsl:value-of select="$local:cur-player-pos" />
                      <xsl:value-of select="$local:pick-pos" />
                      <xsl:value-of select="$local:player" />
                      <xsl:value-of select="$local:orientation" />
                    </div>
                    -->
                    <xsl:apply-templates select="/game/draft/deck[@player=$local:player]/circle[@booster=$local:booster]/card[((position() - 1 + $local:orientation * (($local:cur-player-pos - 1) - ($local:player-pos - 1))  - ($local:pick-pos - 1)) mod $local:num = 0) and (position() >= $local:pick-pos)]" >
                      <xsl:with-param name="local:set" select="$local:set"/>
                      <xsl:with-param name="local:is-active-player" select="$local:player-pos = $local:cur-player-pos"/>
                    </xsl:apply-templates>

                  </xsl:for-each>

                </div>
                </xsl:for-each>
            </div>
            </xsl:for-each>
        </div>
      </xsl:for-each>

    </div>

    <div class="preview">
      <img id="dv_card" class="card-preview" alt="" src="http://mymagic.ru/assets/images/site_tools/dv_null.jpg" />
      <img id="dv_card_back" class="card-preview" alt="" src="http://mymagic.ru/assets/images/site_tools/dv_null.jpg" />
      <div style="clear: both;" ><a href="javascript:void(0);" class="dv_text_link">Смотреть все пики &gt;&gt;</a></div>
    </div>

  </div>

</div>
</body>
</html>
</xsl:template>

</xsl:stylesheet>
