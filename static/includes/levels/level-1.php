<div class="level" id="level1">
	<div class="level-section" id="section-bank" data-progress="10">
		<h3 class="text-center">Select Your <strong>Bank or Card</strong></h3><br/>
		<select name="bank" class="form-control">
			<option value=""></option>
			<option>Wells Fargo</option>
			<option>Bank of America</option>
		</select><br/>
		<button class="btn btn-default buttonInside pull-right" onclick="showSection('account')">
			NEXT &nbsp;<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
		</button>
		<div class="clearfix"></div>
	</div>
	<div class="level-section" id="section-account" data-progress="20">
		<h3 class="text-center">Connect Your <strong>Accounts</strong></h3><br/>
		<a onclick="showSection('bank')" class="form-control form-control-inverted">
			You are connected to: <span class="bank"></span>
			<span class="glyphicon glyphicon-pencil pull-right" aria-hidden="true"></span>
		</a>
		<p style="margin-left:15px;"><strong>NOTE:</strong> For this you will need your credentials for your online banking account.</p>
		<div class="form-horizontal">
			<div class="form-group">
				<div class="col-sm-12">
					<input type="text" class="form-control" placeholder="Username: Direct to Bank">
				</div>
			</div>
			<div class="form-group">
				<div class="col-sm-12">
					<input type="password" class="form-control" placeholder="Password">
				</div>
			</div>
		</div>
		
		<button class="btn btn-default buttonInside pull-left" onclick="showSection('bank')">
			<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>&nbsp; BACK 
		</button>
		<button class="btn btn-default buttonInside pull-right" onclick="showSection('final')">
			NEXT &nbsp;<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
		</button>
		<div class="clearfix"></div>
	</div>
	<div class="level-section" id="section-final" data-progress="30">
		<h3 class="text-center">Connect <strong>Your Accounts</strong></h3><br/>
		<a onclick="showSection('bank')" class="form-control form-control-inverted">
			You are connected to: <span class="bank"></span>
			<span class="glyphicon glyphicon-pencil pull-right" aria-hidden="true"></span>
		</a>
		<p class="text-center">Check the card/account you would like to use.</p>
		<div class="checkbox text-center">
			<label>
		    	<input type="checkbox" value="">
				Account Ending in <strong>6503</strong>
			</label>
		</div>
		<div class="checkbox text-center">
			<label>
		    	<input type="checkbox" value="">
				Account Ending in <strong>2456</strong>
			</label>
		</div><br/>
		<p class="text-center">
			<button class="btn btn-default buttonInside" onclick="showLevel(2, 'intro')">STEP 2: CHOOSE HOW TO INVEST &nbsp;<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span></button>
		</p>
	</div>
</div>