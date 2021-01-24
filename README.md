
# Shortened Url
### Preface
- Create a url-shortening service
- The pathname of a shortened url is less than or equal to five characters
- Support at least ten million urls
- Display the preview of a url

### Tools
- MySQL
- Python + Flask

### Environment
- Install Python
	1. install python - https://www.python.org/downloads/
	2. pip install virtualenv
	3. cd ~
	4. git clone https://github.com/CheHaoKang/Shortened_Url.git
	5. cd Shortened_url
	6. virtualenv venv
	7. source venv/bin/activate
	8. pip install -r requirements.txt
	9. python teaches.py
	10. surf to http://127.0.0.1:5000/

- Install MySQL
	1. https://dev.mysql.com/downloads/installer/
	2. cd ~/Shortened_url
	3. mysql -u root -p < shortened_url_2021-01-24.sql

### Usage and Design
- Input a url which will be shortened
![](https://i.imgur.com/7xPCPMT.png)[](https://i.imgur.com/7xPCPMT.png)
- Click **Submit**
- A preview and shortened url appear
![](https://i.imgur.com/S7BScVe.png)[](https://i.imgur.com/S7BScVe.png)
- Prevent **url_id** corruption
	- Use **lock** table to only allow one process to update **url_mapping** table
- Use **base-52** to transform a **url_id** into characters
	- {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'j', 10: 'k', 11: 'l', 12: 'm', 13: 'n', 14: 'o', 15: 'p', 16: 'q', 17: 'r', 18: 's', 19: 't', 20: 'u', 21: 'v', 22: 'w', 23: 'x', 24: 'y', 25: 'z', 26: 'A', 27: 'B', 28: 'C', 29: 'D', 30: 'E', 31: 'F', 32: 'G', 33: 'H', 34: 'I', 35: 'J', 36: 'K', 37: 'L', 38: 'M', 39: 'N', 40: 'O', 41: 'P', 42: 'Q', 43: 'R', 44: 'S', 45: 'T', 46: 'U', 47: 'V', 48: 'W', 49: 'X', 50: 'Y', 51: 'Z'}
	- if the **url_id** is **250**, the shortened url is **eQ**.

### Should have done
- Hook to Nginx for load balancing
- Create a database connection only at the beginning of **teaches.py**

### Unit Test
- Test if urls are shortened correctly
- Multi-processes pressure testing
- Steps
	- cd ~/Shortened_url
	- pytest