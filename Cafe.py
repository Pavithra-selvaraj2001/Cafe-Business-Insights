#!/usr/bin/env python
# coding: utf-8
"""
Domain  : Retail 
Dataset : cafe
Findings: 
     1. Status of Product(Active/Discontinued)
     2. Analyzing trends across discount values
     3. Top Ordered Categories by Country
     4. Timeliness of Customer Deliveries
     5. Revenue generation and profit analyzation
"""
# In[21]:


# import packages


# In[23]:


import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# In[25]:


#reading the csv file (having encoded utf-8 issues)


# In[27]:


cafe_customers = pd.read_csv("cafe_customers.csv", encoding='ISO-8859-1')
cafe_products = pd.read_csv("cafe_products.csv", encoding = 'ISO-8859-1')
categories = pd.read_csv("categories.csv", encoding = 'ISO-8859-1')
Copy_data_dictionary = pd.read_csv("Copy of data_dictionary.csv", encoding = 'ISO-8859-1')
employees = pd.read_csv("employees.csv", encoding = 'ISO-8859-1')
order_details = pd.read_csv("order_details.csv", encoding = 'ISO-8859-1')
orders = pd.read_csv("orders.csv", encoding = 'ISO-8859-1')
shippers = pd.read_csv("shippers.csv", encoding = 'ISO-8859-1')


# In[29]:


#Load Data


# In[31]:


#Merge the cafe_products and categories by [categoryID]

#Status of Product(Active/Discontinued)

product_categories = pd.merge(cafe_products, categories, on = 'categoryID', how='left')


# In[33]:


#product_categories[product_categories['discontinued']==1]
#product_categories = product_categories[product_categories['discontinued']==0]


# In[35]:


product_categories = product_categories.groupby(['categoryName','productName'])[['discontinued']].mean().reset_index()


# In[37]:


status_count = product_categories.pivot_table(index='categoryName', 
                              columns='discontinued', 
                              aggfunc='size',
                              fill_value=0
                                             )

status_count


# In[39]:


# Fill NaN in discontinued column as 0 (assume active if missing)
product_categories['discontinued'] = product_categories['discontinued'].fillna(0)

# Create pivot table
status_count = product_categories.pivot_table(index='categoryName', 
                              columns='discontinued', 
                              aggfunc='size',
                              values = 'productName',
                              fill_value=0)

# Renaming the columns
status_count.columns = ['Active', 'Discontinued'] if 0.0 in status_count.columns and 1.0 in status_count.columns else status_count.columns

# Plot stacked bar
status_count.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#4caf50', '#f44336'])
plt.title("Product Status by Category")
plt.xlabel("Category")
plt.ylabel("Number of Products")
plt.xticks(rotation=45)
plt.legend(title='Status')
plt.tight_layout()
plt.show()


# In[118]:


# Concatenation of dataframes for easy reference


# In[41]:


product_order_details = pd.merge(cafe_products, order_details, on = 'unitPrice', how='left')


# In[42]:


product_order_details = pd.merge(orders,product_order_details, on ='orderID', how = 'right')


# In[43]:


product_order_details = pd.merge(cafe_customers,product_order_details, on ='customerID', how = 'right')


# In[44]:


product_order_details = pd.merge(employees,product_order_details, on ='employeeID', how = 'right')


# In[45]:


product_order_details = pd.merge(product_categories, product_order_details, on='discontinued', how = 'right')


# In[51]:


product_order_details = pd.merge(shippers,product_order_details, on ='shipperID', how = 'right')


# In[53]:


product_order_details


# In[55]:


#Analyzing trends across discount values


# In[56]:


order_based_df = product_order_details[['productName_x','country_y','city_y','categoryName','quantity','discount','companyName_y','orderID']]

# Taking the discount value > 0.0
order_based_df = order_based_df[order_based_df['discount']>0.0]

# Renaming the column names
order_based_df.columns = ['ProductName','Country','City','CategoryName','Quantity','Discount','CompanyName','OrderId']

order_based_df


# In[57]:


discount_based_df = order_based_df.groupby(['CompanyName','CategoryName','Country'])[['Discount']].max().reset_index()


# In[58]:


fig = px.treemap(
    discount_based_df,
    path=['Country', 'CategoryName','CompanyName'],
    values='Discount',
    color='Country',
    title='Top Discounts Across Countries',
    hover_data={'Discount': True}
)

fig.show()


# In[59]:


# Top Ordered Categories by Country

order_df = order_based_df.groupby(['Country','ProductName'])[['OrderId']].count().reset_index()

order_df.head()


# In[60]:


# Taking the max count of the order across the country

top_products = order_df.sort_values(['Country', 'OrderId'], ascending=[True, False])
top_products = top_products.groupby('Country').head(3).reset_index(drop=True)


# In[62]:


fig = px.pie(
    top_products,
    values = 'OrderId',
    names = 'Country',
    hover_data=['ProductName'],
    title = 'Frequent order on the highest product',
)

fig.update_layout(
    width = 600,
    height = 600
)


fig.show()


# In[63]:


# Timeliness of Customer Deliveries


# In[66]:


shipper_df = product_order_details[['orderDate','requiredDate','shippedDate','companyName_x']].copy()


# In[69]:


shipper_df.columns = ['OrderDate','RequiredDate','ShippedDate','Shipper_CompanyName']
shipper_df


# In[70]:


#datetime conversion

shipper_df['RequiredDate'] = pd.to_datetime(shipper_df['RequiredDate'])
shipper_df['ShippedDate'] = pd.to_datetime(shipper_df['ShippedDate'])
shipper_df['OrderDate'] = pd.to_datetime(shipper_df['OrderDate'])
shipper_df.dropna(inplace=True)

#On-time delivery

shipper_df['On-time'] = shipper_df['ShippedDate'] <= shipper_df['RequiredDate']


# In[71]:


#Early Delivery

shipper_df['Early_delivery'] = (shipper_df['RequiredDate'] - shipper_df['ShippedDate']).dt.days
shipper_df['Early_delivery'] = shipper_df['Early_delivery'].apply(lambda x:x if x>0 else 0)


# In[72]:


#Late Delivery

shipper_df['Late_delivery'] = (shipper_df['ShippedDate'] - shipper_df['RequiredDate']).dt.days
shipper_df['Late_delivery'] = shipper_df['Late_delivery'].apply(lambda x:x if x>0 else 0)


# In[73]:


shipper_df = shipper_df[['Shipper_CompanyName','On-time','Late_delivery','Early_delivery']]
shipper_df = shipper_df.groupby(['Shipper_CompanyName']).agg({
    'On-time':'sum',
    'Late_delivery':'sum',
    'Early_delivery':'sum'
})

shipper_df


# In[74]:


shipper_df = shipper_df.reset_index()


# In[75]:


shipper_df = shipper_df.melt(
    id_vars = 'Shipper_CompanyName',
    value_vars = ['On-time','Late_delivery','Early_delivery'],
    var_name = 'Delivery Status',
    value_name = 'Delivery Count'
)


# In[76]:


fig = px.bar(
    shipper_df,
    x='Shipper_CompanyName',
    y='Delivery Count',
    color='Delivery Status',
    text='Delivery Count',
    barmode='group',
    title='On-Time, Early, or Late? Delivery Insights',
    color_discrete_map={
        'On-time':'#90CAF9',
        'Early_delivery':'#4CAF50',
        'Late_delivery':'#F44336'
    }
)

fig.update_traces(textposition='outside')  # place labels above bars
fig.update_layout(
    xaxis_title='Shipment Company Name',
    yaxis_title='Delivery Count'
)
fig.show()


# In[77]:


# Revenue generation and profit analyzation

revenue_df = product_order_details[['quantity','unitPrice','freight','categoryName','discount','country_y']].copy()
revenue_df.columns = ['Quantity','UnitPrice','Freight','CategoryName','Discount','Country']


# In[78]:


#calculation the revenue

revenue_df['Quantity_price'] = revenue_df['Quantity'] * revenue_df['UnitPrice'] * (1 - revenue_df['Discount'])


# In[79]:


#calculating the profit

revenue_df['Profit'] = revenue_df['Quantity_price'] - revenue_df['Freight']
revenue_df.head(1)


# In[80]:


revenue_df = revenue_df.groupby(['CategoryName','Country']).agg({
    'Quantity_price':'max',
    'Profit':'max'
}).reset_index()

revenue_df


# In[81]:


fig = px.line(
    revenue_df,
    x='CategoryName',
    y='Quantity_price',
    markers=True,
    title='Revenue vs Profit Across Regions',
    hover_data={
        'CategoryName': True,
        'Quantity_price': True,
        'Country': True,
        'Profit' : True
    }
)

fig.update_traces(line=dict(color='white', dash='dash'), marker=dict(symbol='circle'))

fig.update_layout(
    xaxis_title='Category',
    yaxis_title='Revenue and Profit',
    template='plotly_dark'
)

fig.show()    


# In[82]:


# Save the file (.csv) format


# In[83]:


revenue_df.to_csv("revenue_and_Profit.csv", index= False)


# In[84]:


shipper_df.to_csv("Delivery_timeline.csv", index= False)


# In[85]:


top_products.to_csv("Frequent_order.csv", index=False)


# In[120]:


discount_based_df.to_csv("discount_order.csv", index = False)


# In[87]:


product_categories.to_csv("discontinued_product.csv", index = False)


# In[88]:


#optional
product_order_details.to_csv("product_details.csv", index=False)


# In[ ]:





# In[ ]:




