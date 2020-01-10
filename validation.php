<!DOCTYPE html>
<html>
<head>
  <title>NGA Kanmusu Saimoe Monitor</title>
  <meta charset="utf-8">
  <link rel="icon" href="nga.ico">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://cdn.staticfile.org/twitter-bootstrap/4.1.0/css/bootstrap.min.css">
  <script src="https://cdn.staticfile.org/jquery/3.2.1/jquery.min.js"></script>
  <script src="https://cdn.staticfile.org/popper.js/1.12.5/umd/popper.min.js"></script>
  <script src="https://cdn.staticfile.org/twitter-bootstrap/4.1.0/js/bootstrap.min.js"></script>
  <script src="https://cdn.staticfile.org/Chart.js/2.7.3/Chart.bundle.min.js"></script>
  <style type="text/css">a.btn{margin-bottom: 1rem;} hr{margin: 1rem;} .jumbotron{padding-bottom: 1rem}</style>
</head>
<body>

<div class="jumbotron text-center">
  <h1>NGA舰萌 投票监控</h1>
  <p>人工验证</p>
</div>
 
<div class="container">
  <div class="row">
    <div class="col-sm-2 text-center">
      <ul class="list-group position-fixed" id="sidebar">
      </ul>
    </div>
    <div class="col-sm-10 text-center">
      <p>记录表格</p>
      <table class="table table-striped table-borded table-hover">
        <thead><tr>
          <th width="64px">楼层</th>
          <th>回帖内容</th>
          <th width="80px">投票数</th>
          <th width="80px">分词数</th>
        </tr></thead>
        <tbody>
<?php
  $file=fopen("validation.log","r") or exit("Unable to open file!");
  while(!feof($file)){
    $line = fgets($file);
    if(strlen($line) < 2)
      continue;
    else if(strpos($line, "------>") !== false){
      $line = str_replace("------> output/", "", $line);
      $line = str_replace("-validation.csv\n", "", $line);
      echo "<tr><td></td><td><b id=\"" . $line . "\">" . $line . "</b></td><tr>";
    }
    else if(strpos($line, "超票") !== false){
      $line = str_replace("超票\t", "", $line);
      $line = str_replace("\t", "</td><td>", $line);
      echo "<tr><td>" . $line . "</td><td>超票</td></tr>";
    }
    else{
      $line = str_replace("\t", "</td><td>", $line);
      echo "<tr><td>" . $line . "</td></tr>";
    }
  }
  fclose($file);
?>      
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
  window.onload = function() {
    groups = $('b');
    for ( i = 0; i < groups.length ; i ++){
      var gname = groups[i].id.split('-');
      $("#sidebar").append('<a class="list-group-item" href="#' + groups[i].id + '">Group ' + gname[gname.length-1]+'</a>');
    }
  };
</script>
</body>
</html>