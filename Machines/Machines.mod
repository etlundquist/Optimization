/*********************************************
 * Two Products Three Machines Problem
 * Author: elundquist
 *********************************************/
 
// 1. set up the input variables
//------------------------------
 
{string} Products = ...;
{string} Machines = ...;
 
int MinQuantity[Products] = ...;
int MaxQuantity[Products] = ...;
int UnitProfits[Products] = ...;
 
int   MaxCapacity[Machines] = ...;
float UnitCapacity[Products][Machines] = ...;
int   FixedCosts = ...;
 
// 2. set up the decision variables
//---------------------------------
 
dvar int Quantity[Products];
 
// 3. set up the objective function
//---------------------------------
 
maximize 
  sum (p in Products)
    Quantity[p] * UnitProfits[p] - FixedCosts; 
    
// 4. set up the constraints
//--------------------------

subject to {

	forall (p in Products) ctMinQuantity:
		Quantity[p] >= MinQuantity[p];
		
	forall (p in Products) ctMaxQuantity:
		Quantity[p] <= MaxQuantity[p];
		
	forall (m in Machines) ctMaxCapacity: 
		sum (p in Products) 
			UnitCapacity[p][m] * Quantity[p] <= MaxCapacity[m];  
			 			       
}
  
 	
