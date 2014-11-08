# -*- coding: utf-8 -*-
valid_body = u"""
     <div class="reports">
        <div class="reportsLine noBorder">
 
 <span class="status">&nbsp;</span>
<div class="DateWithTransaction">
    <div class="dateCaption">
        <span data-action="change" data-params="{&quot;mode&quot;:&quot;replace&quot;,&quot;data&quot;:{&quot;SortOrder&quot;:1}}">
            Дата
             ↓
        </span>
    </div>
    <div class="transactionCaption">Транзакция</div>
</div>
<div class="IncomeWithExpendCaptions">
    <div class="incomeCaption">
        <span data-action="change" data-params="{&quot;mode&quot;:&quot;replace&quot;,&quot;data&quot;:{&quot;SortOrder&quot;:18}}">
            Приход
 
        </span>
    </div>
    <div class="expendCaption">
        <span data-action="change" data-params="{&quot;mode&quot;:&quot;replace&quot;,&quot;data&quot;:{&quot;SortOrder&quot;:54}}">
            Расход
 
        </span>
    </div>
    <div class="commissionCaption">Комиссия</div>
</div>
<div class="originalExpenseCaption">
    <span data-action="change" data-params="{&quot;mode&quot;:&quot;replace&quot;,&quot;data&quot;:{&quot;SortOrder&quot;:486}}">
        Сумма в валюте операции
 
    </span>
</div>
<div class="ProvWithComment">
    <div class="providerCaption">
        <span data-action="change" data-params="{&quot;mode&quot;:&quot;replace&quot;,&quot;data&quot;:{&quot;SortOrder&quot;:6}}">
            Провайдер
 
        </span>
        <span class="opNumber" data-action="change" data-params="{&quot;mode&quot;:&quot;replace&quot;,&quot;data&quot;:{&quot;SortOrder&quot;:162}}">
            Номер
 
        </span>
    </div>
    <div class="commentCaption">Комментарий</div>
</div>
<div class="clearBoth"></div>
        </div>
 
 
 <div class="reportsLine status_SUCCESS" data-container-name="item">
    <i class="icon icon_SUCCESS fa fa-check-circle"></i>
    <i class="icon icon_ERROR fa fa-times-circle"></i>
    <i class="icon icon_PROCESSED fa fa-clock-o"></i>
 
 	<div class="DateWithTransaction">
	    <span class="date">10.08.2014</span>
	    <span class="time">20:14:44</span>
 
	        <div class="transaction">999999900352844497</div>
 
	</div>
 
 	    <div class="IncomeWithExpend expenditure">
	        <div class="cash">2,00 руб. </div>
	        <div class="commission">
 	        </div>
 
 	            <div class="operations"><a target="_blank" href="/report/cheque.action?transaction=4798750641&amp;direction=OUT" class="cheque">Распечатать чек</a></div>
 	    </div>
 	<div class="originalExpense">
	    <span>2,00 руб. </span>
	</div>
 	<div class="ProvWithComment">
	    <div class="provider">
	        <span>Visa QIWI Wallet</span>
	        <span class="opNumber"> some info</span>
	    </div>
	    <div class="comment"> nc _123-456</div>
	</div>
	<div class="clearBoth"></div>
	<div class="extra" data-container-name="item-extra">
		<div class="item">
	        <span class="key">Транзакция:</span>
	        <span class="value">999999900352844497</span>
	    </div>
	</div>
</div>
 
 
 <div class="reportsLine status_SUCCESS" data-container-name="item">
    <i class="icon icon_SUCCESS fa fa-check-circle"></i>
    <i class="icon icon_ERROR fa fa-times-circle"></i>
    <i class="icon icon_PROCESSED fa fa-clock-o"></i>
 
 	<div class="DateWithTransaction">
	    <span class="date">10.08.2014</span>
	    <span class="time">20:12:51</span>
 
	        <div class="transaction">999999900352843708</div>
 
	</div>
 
 	    <div class="IncomeWithExpend expenditure">
	        <div class="cash">1,00 руб. </div>
	        <div class="commission">
 	        </div>
 
 	            <div class="operations"><a target="_blank" href="/report/cheque.action?transaction=4798746524&amp;direction=OUT" class="cheque">Распечатать чек</a></div>
 	    </div>
 	<div class="originalExpense">
	    <span>1 001,50 руб. </span>
	</div>
 	<div class="ProvWithComment">
	    <div class="provider">
	        <span>Visa QIWI Wallet</span>
	        <span class="opNumber"> some info</span>
	    </div>
	    <div class="comment">234-567</div>
	</div>
	<div class="clearBoth"></div>
	<div class="extra" data-container-name="item-extra">
		<div class="item">
	        <span class="key">Транзакция:</span>
	        <span class="value">999999900352843708</span>
	    </div>
	</div>
</div>


 <div class="reportsLine status_SUCCESS" data-container-name="item">
    <i class="icon icon_SUCCESS fa fa-check-circle"></i>
    <i class="icon icon_ERROR fa fa-times-circle"></i>
    <i class="icon icon_PROCESSED fa fa-clock-o"></i>

 	<div class="DateWithTransaction">
	    <span class="date">10.08.2014</span>
	    <span class="time">20:12:51</span>

	        <div class="transaction">123456</div>

	</div>

 	    <div class="IncomeWithExpend expenditure">
	        <div class="cash">1,00 руб. </div>
	        <div class="commission">
 	        </div>

 	            <div class="operations"><a target="_blank" href="/report/cheque.action?transaction=4798746524&amp;direction=OUT" class="cheque">Распечатать чек</a></div>
 	    </div>
 	<div class="originalExpense">
	    <span>1 001,50 руб. </span>
	</div>
 	<div class="ProvWithComment">
	    <div class="provider">
	        <span>Visa QIWI Wallet</span>
	        <span class="opNumber"> some info</span>
	    </div>
	    <div class="comment">234-567</div>
	</div>
	<div class="clearBoth"></div>
	<div class="extra" data-container-name="item-extra">
		<div class="item">
	        <span class="key">Транзакция:</span>
	        <span class="value">999999900352843708</span>
	    </div>
	</div>
</div>


 <div class="reportsLine status_SUCCESS" data-container-name="item">
    <i class="icon icon_SUCCESS fa fa-check-circle"></i>
    <i class="icon icon_ERROR fa fa-times-circle"></i>
    <i class="icon icon_PROCESSED fa fa-clock-o"></i>

 	<div class="DateWithTransaction">
	    <span class="date">10.08.2014</span>
	    <span class="time">20:12:51</span>

	        <div class="transaction"></div>

	</div>

 	    <div class="IncomeWithExpend expenditure">
	        <div class="cash">1,00 руб. </div>
	        <div class="commission">
 	        </div>

 	            <div class="operations"><a target="_blank" href="/report/cheque.action?transaction=4798746524&amp;direction=OUT" class="cheque">Распечатать чек</a></div>
 	    </div>
 	<div class="originalExpense">
	    <span>1 001,50 руб. </span>
	</div>
 	<div class="ProvWithComment">
	    <div class="provider">
	        <span>Visa QIWI Wallet</span>
	        <span class="opNumber"> some info</span>
	    </div>
	    <div class="comment">234-567</div>
	</div>
	<div class="clearBoth"></div>
	<div class="extra" data-container-name="item-extra">
		<div class="item">
	        <span class="key">Транзакция:</span>
	        <span class="value">999999900352843708</span>
	    </div>
	</div>
</div>
 
 
 <div class="divider"><!--  --></div>
<div class="reportsTotalLine">
 
 
 
        <div class="SuccessWithFail expenditure">
            <div class="success">
                3,00
                руб.
            </div>
            <div class="fail">0,00</div>
        </div>
        <div class="SuccessWithFail income">
            <div class="success">
                0,00
                руб.
            </div>
            <div class="fail">0,00</div>
        </div>
             <div class="SuccessWithFailCaption">
                <div class="successCaption">Итого:</div>
                <div class="failCaption">Не успешно:</div>
            </div>
 
        <div class="originalExpense">
            <div class="success">&nbsp;</div>
            <div class="fail">&nbsp;</div>
        </div>
         <div class="clearBoth"></div>
 
 </div>
 
    </div>
 """