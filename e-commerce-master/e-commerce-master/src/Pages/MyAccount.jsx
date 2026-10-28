import { Box, Heading, Text } from "@chakra-ui/react";
import React from "react";
import { useSelector } from "react-redux";
const MyAccount = () => {
  const profileData = useSelector((state) => state.AuthReducer?.profileData);
  return (
    <div>
      <Box
        m="2rem"
        className="myaccount"
        h={"100vh"}
        bgImage={"linear-gradient(skyblue,royalblue)"}
      >
        <Heading w={"80%"} m={"auto"} className="heading">
          Hi! {profileData.length !== 0 ? profileData.name : "User"}! Thank you
          for visiting our website. We hope you enjoy shopping with us.
        </Heading>
        <Text fontSize={"30px"} color="white">
          Have A Great Day!
        </Text>
      </Box>
    </div>
  );
};

export default MyAccount;
