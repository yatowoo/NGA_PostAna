<!DOCTYPE html>
<html>
<head>
  <title>NGA Kanmusu Saimoe Monitor</title>
  <meta charset="utf-8">
  <link rel="icon" href="nga.ico">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://cdn.staticfile.org/twitter-bootstrap/4.4.1/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://mladenplavsic.github.io/bootstrap-navbar-sidebar/navbar-fixed-left.min.css">
  <script src="https://cdn.staticfile.org/jquery/3.2.1/jquery.min.js"></script>
  <script src="https://cdn.staticfile.org/popper.js/1.12.5/umd/popper.min.js"></script>
  <script src="https://cdn.staticfile.org/twitter-bootstrap/4.4.1/js/bootstrap.min.js"></script>
  <script src="https://cdn.staticfile.org/Chart.js/2.7.3/Chart.bundle.min.js"></script>
  <style type="text/css">a.btn{margin-bottom: 1rem;} hr{margin: 1rem;} .jumbotron{padding-bottom: 1rem}</style>
</head>
<body>
<nav class="navbar navbar-expand-md navbar-dark bg-primary fixed-left">
  <a class="navbar-brand" href="">NGA_SAIMOE</a>
  <button class="navbar-toggler collapsed" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="navbar-collapse collapse" id="navbarsExampleDefault" style="">
    <ul class="navbar-nav" id="sidebar">
    </ul>
  </div>
</nav>


<div class="container">
    <div class="jumbotron text-center">
      <h1>NGA舰萌 投票监控</h1>
      <p>人工验证 分词失败回帖内容记录表格</p>
    </div>
    <div class="table-responsive text-center">
      <table class="table table-striped table-borded table-hover">
        <thead>
        <tr>
          <th>楼层</th>
          <th>回帖内容</th>
          <th>投票数</th>
          <th>分词数</th>
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
      echo "<tr><td></td><td><b id=\"" . $line . "\">" . $line . "</b></td><td></td><td></td><tr>";
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

<script>
  window.onload = function() {
    groups = $('b');
    for ( i = 0; i < groups.length ; i ++){
      var gname = groups[i].id.split('-');
      $("#sidebar").append('<a class="nav-link" href="#' + groups[i].id + '">Group ' + gname[gname.length-1]+'</a>');
    }
  };
</script>
</body>
</html>