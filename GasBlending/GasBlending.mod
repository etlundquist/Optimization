// Gas Blending Model
// Author: Eric Lundquist

// 1. set up the input variables
//------------------------------

// define tuple data structures for raw/blended gas with relevant attributes

tuple RawGas {
	int   Octane;
	int   Available;
	float PurchasePrice;
	float ResalePrice;
};

tuple BlendGas {
	int   Octane;
	float SalePrice;
	int   MinQuantity;
	int   MaxQuantity; 	
};

// define sets of the raw/blended gas types we'll need for this problem instance

{string} RawTypes   = ...;
{string} BlendTypes = ...;

// define tuple arrays to hold all of the data we'll need for the problem

RawGas   Raw[RawTypes]     = ...; 
BlendGas Blend[BlendTypes] = ...; 

// 2. set up the decision variables
//---------------------------------

dvar float+ QuantityBlend[RawTypes][BlendTypes];
dvar float+ QuantityResale[RawTypes];
// NOTE: these are actually not constrained to be integers in the original problem
// NOTE: my profit result matches the Excel model, but the blend allocations are different?

// 3. set up the objective function
//---------------------------------

maximize 

sum (r in RawTypes, b in BlendTypes) // profit from selling blended gas
	(QuantityBlend[r][b]*Blend[b].SalePrice - QuantityBlend[r][b]*Raw[r].PurchasePrice) + 
sum (r in RawTypes)                  // profit from selling raw gas
	(QuantityResale[r]*Raw[r].ResalePrice - QuantityResale[r]*Raw[r].PurchasePrice);
	
// 4. set up the constraints
//--------------------------

subject to {

// the amount blended and resold can't be more than the total available
forall (r in RawTypes) ctAvailable:
	sum (b in BlendTypes)
	  QuantityBlend[r][b] + QuantityResale[r] <= Raw[r].Available;
	  
// min market demand constraint for each blend type
forall (b in BlendTypes) ctMinQuantity:
	sum (r in RawTypes)
	  QuantityBlend[r][b] >= Blend[b].MinQuantity;

// max market demand constraint for each blend type	  
forall (b in BlendTypes) ctMaxQuantity:
	sum (r in RawTypes)
	  QuantityBlend[r][b] <= Blend[b].MaxQuantity;	

// minimum octane requirements constraint  
forall (b in BlendTypes) ctOctane:
	sum (r in RawTypes)
	  (Raw[r].Octane - Blend[b].Octane) * QuantityBlend[r][b] >= 0;  
	  
}





