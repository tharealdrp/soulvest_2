<nav class="navbar navbar-default" id="soulnav">
	<div class="container">
		<div class="navbar-header">
			<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
				<span class="sr-only">Toggle navigation</span>
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
			</button>
			<a class="navbar-brand animated bounceInLeft" href="home.php">
				<img src="images/logo-1.png" class="img-responsive" width="166" height="42" alt=""/>
			</a>
		</div>
	
		<div class="collapse navbar-collapse animated fadeIn" id="bs-example-navbar-collapse-1">
			<ul class="nav navbar-nav navbar-right">
				<li><a href="portfolios.php">PORTFOLIOS</a></li>
				<li><a href="faq.php">FAQ</a></li>
				<li><a href="about.php">ABOUT</a></li>
                
                <li><button type="button" class="btn btn-primary btn-lg button1 buttonNavMargin"  onclick="window.location='signup.php'">SIGN UP</button></li>
				<li><button  type="button" class="btn btn-primary btn-lg button1 buttonNavMargin" onclick="loadDemo()">TOUR THE APP</button>&nbsp;</li>
                <li><a href="home.php" class="homeIcon"><img src="images/home.png"  width="24px"/></a></li>
			</ul>
		</div>
		
		<div class="hidden">
			<a href="images/dash1.jpg" class="fancybox fancybox-demo" rel="demo"></a>
			<a href="images/dash2.jpg" class="fancybox fancybox-demo" rel="demo"></a>
			<script type="text/javascript">
				function loadDemo(){
					$(".fancybox-demo").eq(0).click();
				}
			</script>
		</div>
	</div>
</nav>