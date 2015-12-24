/*********************************************
 * Brewer Problem (Quantities of Ale & Beer)
 * Author: elundquist
 *********************************************/
 
// 1. set up the input variables
//------------------------------
 
{string} Products = ...;     
{string} Ingredients = ...;  

int UnitProfits[Products] = ...; 
int UnitIngredients[Products][Ingredients] = ...; 
int MaxIngredients[Ingredients] = ...;

// 2. set up the decision variables
//---------------------------------

dvar int Quantity[Products];

// 3. set up the objective function
//---------------------------------

maximize 
  sum (p in Products)
    Quantity[p] * UnitProfits[p];            
 
// 4. set up the constraints
//--------------------------

subject to {
	forall (i in Ingredients) ctMaxIngredients: 
		sum (p in Products) 
			UnitIngredients[p][i] * Quantity[p] <= MaxIngredients[i];          
}

 

